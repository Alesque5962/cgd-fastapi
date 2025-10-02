import sys
import asyncio
import os
import random
from typing import Annotated
import dagger
from dagger import DefaultPath, Doc, dag, function, object_type, Ignore

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
    async def build_image(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Doc("cgd-backend source directory"),
            ignored,
        ],
    ) -> dagger.Container:
        """Build l'image Docker"""
        self.run_tests(source)  # Exécute les tests avant de build
        print("🏗️ Construction de l'image Docker...")
        # Stage 1: Build
        try:
            builder = (
                dag.container()
                .from_("python:3.12.8-slim")
                .with_mounted_cache("/root/.cache/uv", dag.cache_volume("uv-cache"))
                .with_directory("/app", source)
                .with_workdir("/app")
                # Installation de uv
                .with_exec(["pip", "install", "uv"])
                # Copie des fichiers de configuration
                .with_file("/app/pyproject.toml", source.file("pyproject.toml"))
                .with_file("/app/uv.lock", source.file("uv.lock"))
                .with_file("/app/README.md", source.file("README.md"))
                # Installation des dépendances
                .with_exec(["uv", "sync", "--frozen", "--no-dev"])
            )

            # Stage 2: Production
            return await (
                dag.container()
                .from_("python:3.12.8-slim")
                .with_workdir("/app")
                .with_directory("/app", builder.directory("/app"))
                .with_env_variable("PATH", "/app/.venv/bin:$PATH")
                .with_exposed_port(8000)
                .with_entrypoint(
                    [
                        "fastapi",
                        "run",
                        "cgd_backend.main:app",
                        "--host",
                        "0.0.0.0",
                        "--port",
                        "8000",
                    ]
                )
            )
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'image Docker : {str(e)}")
            raise

    @function
    async def publish(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Doc("cgd-backend source directory"),
            ignored,
        ],
    ) -> str:
        """Publie l'image Docker sur DockerHub"""

        # Lecture du fichier .env depuis le répertoire source
        try:
            # Attendre le contenu du fichier avec await
            env_content = await source.file(".env").contents()

            # Parsing des variables d'environnement
            env_vars = {}
            for line in env_content.splitlines():
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("\"'")

            # Récupération des credentials Docker
            docker_username = env_vars.get("DOCKER_USERNAME", "")
            docker_password = dag.set_secret(
                "docker_password", env_vars.get("DOCKER_PASSWORD", "")
            )

        except Exception as e:
            print(f"❌ Erreur lors de la lecture du .env file : {str(e)}")
            raise

        if not docker_username or not docker_password:
            raise ValueError(
                "Variables DOCKER_USERNAME et DOCKER_PASSWORD manquantes dans .env file"
            )

        image_ref = f"{docker_username}/cgd-backend:latest"
        print("📤 Publication sur DockerHub...")
        build_image = await self.build_image(source)
        try:
            build_image.with_registry_auth(
                "docker.io", docker_username, docker_password
            ).publish(image_ref)
            return f"✅ Image publiée avec succès : {image_ref}"
        except Exception as e:
            print(f"❌ Erreur lors de la publication de l'image : {str(e)}")
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
            return await (
                self.build_env_tests(source)
                .with_env_variable("PRODUCTION", "true")
                .with_exec(["uv", "run", "pytest"])
                .stdout()
            )
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution des tests : {str(e)}")
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
        """Build a ready-to-use development environment"""
        try:
            return await (
                dag.container()
                .from_("python:3.12-slim")
                .with_workdir("/app")
                .with_directory("/app", source)
                .with_exec(["pip", "install", "uv"])
                .with_exec(["uv", "sync"])
            )
        except Exception as e:
            print(f"❌ Erreur lors du build de l'environnement de tests : {str(e)}")
            raise


""" @object_type
class CgdBackend:
    @function
    def test_container(self) -> dagger.Container:
        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_mounted_directory(
                "/app",
                dag.host().directory(
                    ".", exclude=["__pycache__", "*.pyc", ".pytest_cache", "mp3_folder"]
                ),
            )
            .with_workdir("/app")
            .with_exec(["pip", "install", "-e", ".[test]"])
            .with_env_variable("PRODUCTION", "false")
            .with_env_variable("OPENAI_API_KEY", "test-key")
            .with_env_variable("MISTRAL_API_KEY", "test-key")
            .with_env_variable("WHISPER_API_KEY", "test-key")
        )

    @function
    async def run_tests(self) -> str:
        return await self.test_container().with_exec(["pytest", "tests/"]).stdout()

    @function
    def build_image(self) -> dagger.Container:
        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_mounted_directory(
                "/app",
                dag.host().directory(
                    ".", exclude=["__pycache__", "*.pyc", ".pytest_cache", "mp3_folder"]
                ),
            )
            .with_workdir("/app")
            .with_exec(["pip", "install", "."])
            .with_env_variable("PRODUCTION", "true")
        )

    @function
    async def publish(self) -> str:
        image_ref = "alesque29/cgd-backend:latest"

        # Exécuter d'abord les tests
        test_output = await self.run_tests()
        print("📋 Résultats des tests :")
        print(test_output)

        # Si les tests passent, build et publie
        print("🏗️ Construction de l'image...")
        await self.build_image().publish(image_ref)

        return f"✅ Image publiée : {image_ref}" """


""" if __name__ == "__main__":
    docker_username = os.getenv("DOCKER_USERNAME")
    docker_password = os.getenv("DOCKER_PASSWORD")
    sys.exit(
        asyncio.run(
            CgdBackend.docker_build_publish(
                docker_username=docker_username, docker_password=docker_password
            )
        )
    ) """
