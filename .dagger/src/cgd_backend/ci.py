import logging
import os
from typing import Annotated
import asyncio
import dagger
from dagger import DefaultPath, Doc, dag, function, object_type, Ignore

# Configure logging
level = logging.DEBUG
logging.basicConfig(level=level)
logger = logging.getLogger(__name__)

ignored = (
    Ignore(
        [
            ".pytest_cache",
            ".ruff_cache",
            ".venv",
            "__pycache__",
            "mp3_folder",
            "*.pyc",
        ]
    ),
)


@object_type
class CgdBackend:
    @function
    async def get_docker_credentials(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Doc("cgd-backend source directory"),
            ignored,
        ],
    ):
        try:
            docker_username = os.getenv("DOCKER_USERNAME")
            docker_password = os.getenv("DOCKER_PASSWORD")
        except Exception as e:
            logger.error(f"❌ Error reading Docker credentials from env : {str(e)}")
            try:
                # Reading .env file from source directory
                env_content = await source.file(".env").contents()

                # Parsing environment variables
                env_vars = {}
                for line in env_content.splitlines():
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip().strip("\"'")

                # Extracting Docker credentials
                docker_username = env_vars.get("DOCKER_USERNAME")
                docker_password = env_vars.get("DOCKER_PASSWORD")

            except Exception as e:
                logger.error(f"❌ Error reading .env file : {str(e)}")
                raise

        """ docker_password = dag.set_secret("docker_password", docker_password) """
        return docker_username, docker_password

    @function
    async def docker_build_publish(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Doc("cgd-backend source directory"),
            ignored,
        ],
    ) -> str:
        """Build and publish Docker image on DockerHub"""
        await self.run_tests(source)
        docker_username, docker_password = await self.get_docker_credentials(source)
        if not docker_username or not docker_password:
            raise ValueError("Docker credentials cannot be missing")

        # Stage 1: Build stage
        builder = (
            dag.container()
            .from_("python:3.12.8-slim")
            .with_workdir("/app")
            .with_exec(["pip", "install", "uv"])
            # Copy uv configuration files
            .with_directory("/app", source)
            .with_file("/app/pyproject.toml", source.file("pyproject.toml"))
            .with_file("/app/uv.lock", source.file("uv.lock"))
            # Dependancies installation
            .with_mounted_cache("/root/.cache/uv", dag.cache_volume("uv-cache"))
            .with_exec(["uv", "pip", "install", "--system", "-e", "."])
        )

        # Stage 2: Production stage
        container = (
            dag.container()
            .from_("python:3.12.8-slim")
            .with_workdir("/app")
            # Copy application from builder
            .with_directory("/app/cgd_backend", builder.directory("/app/cgd_backend"))
            # Copie system dependancies from builder
            .with_directory("/usr/local", builder.directory("/usr/local"))
            # Configuration
            .with_env_variable("PYTHONPATH", "/app")
            .with_registry_auth("docker.io", docker_username, docker_password)
            .with_exposed_port(8000)
            # Creating a non-root user
            .with_exec(["groupadd", "-r", "app"])
            .with_exec(["useradd", "-r", "-g", "app", "app"])
            .with_exec(["chown", "-R", "app:app", "/app"])
            .with_user("app")
            .with_entrypoint(
                [
                    "python",
                    "-m",
                    "uvicorn",
                    "cgd_backend.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ]
            )
        )

        logger.info("📤 Publication on DockerHub...")
        image_ref = f"{docker_username}/cgd-backend:latest"
        try:
            await container.publish(image_ref)
            return f"✅ Image successfully published : {image_ref}"
        except Exception as e:
            logger.error(f"❌ Error during publication : {str(e)}")
            raise

    @function
    async def run_tests(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Doc("cgd-backend source directory"),
            ignored,
        ],
    ) -> str:
        """Return the result of running pytest"""
        try:
            build_env_tests = await self.build_env_tests(source)
            return await build_env_tests.with_exec(["uv", "run", "pytest"]).stdout()
        except Exception as e:
            logger.error(f"❌ Error during tests execution : {str(e)}")
            raise

    @function
    async def build_env_tests(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Doc("cgd-backend source directory"),
            ignored,
        ],
    ) -> dagger.Container:
        """Build a ready-to-use test environment"""
        try:
            return await (
                dag.container()
                .from_("python:3.12.8-slim")
                .with_workdir("/app")
                .with_directory("/app", source)
                .with_exec(["pip", "install", "uv"])
                .with_exec(["uv", "sync"])
            )
        except Exception as e:
            logger.error(f"❌ Error during test environment build : {str(e)}")
            raise


if __name__ == "__main__":
    backend = CgdBackend()
    asyncio.run(backend.docker_build_publish(dag.host().directory(".")))
