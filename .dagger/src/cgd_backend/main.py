import sys
import asyncio
import dagger
from dagger import DefaultPath, Doc, dag, function, object_type


import random
from typing import Annotated


@object_type
class CgdBackend:
    @function
    async def publish(
        self,
        source: Annotated[
            dagger.Directory, DefaultPath("/"), Doc("cgd-backend source directory")
        ],
    ) -> str:
        """Publish the application container after building and testing it on-the-fly"""
        await self.test(source)
        return await self.build(source).publish(
            f"ttl.sh/hello-dagger-{random.randrange(10**8)}"
        )

    @function
    def build(
        self,
        source: Annotated[
            dagger.Directory, DefaultPath("/"), Doc("cgd-backend source directory")
        ],
    ) -> dagger.Container:
        """Build the application container"""
        build = (
            self.build_env(source)
            .with_exec(["npm", "run", "build"])
            .directory("./dist")
        )
        return (
            dag.container()
            .from_("nginx:1.25-alpine")
            .with_directory("/usr/share/nginx/html", build)
            .with_exposed_port(80)
        )

    @function
    async def test(
        self,
        source: Annotated[
            dagger.Directory, DefaultPath("/"), Doc("cgd-backend source directory")
        ],
    ) -> str:
        """Return the result of running unit tests"""

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
            .stdout()
        )

        """ return await (
            self.build_env(source)
            .with_exec(["npm", "run", "test:unit", "run"])
            .stdout()
        ) """

    @function
    def build_env(
        self,
        source: Annotated[
            dagger.Directory, DefaultPath("/"), Doc("cgd-backend source directory")
        ],
    ) -> dagger.Container:
        """Build a ready-to-use development environment"""
        node_cache = dag.cache_volume("node")
        return (
            dag.container()
            .from_("node:21-slim")
            .with_directory("/src", source)
            .with_mounted_cache("/root/.npm", node_cache)
            .with_workdir("/src")
            .with_exec(["npm", "install"])
        )


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


if __name__ == "__main__":
    sys.exit(asyncio.run(CgdBackend.publish()))
