import os
import sys
import asyncio
import subprocess
from typing import Optional
from bot.utils import logger
from bot.config import settings

class UpdateManager:
    def __init__(self):
        self.branch = "main"
        self.check_interval = settings.CHECK_UPDATE_INTERVAL
        self.is_update_restart = "--update-restart" in sys.argv
        self._configure_git_safe_directory()
        self._check_and_switch_repository()
        self._ensure_uv_installed()

    def _configure_git_safe_directory(self) -> None:
        try:
            current_dir = os.getcwd()
            subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", current_dir],
                check=True,
                capture_output=True
            )
            logger.info("Git safe.directory configured successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to configure git safe.directory: {e}")

    def _ensure_uv_installed(self) -> None:
        try:
            subprocess.run(["uv", "--version"], check=True, capture_output=True)
            logger.info("uv package manager is already installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("Installing uv package manager...")
            try:
                curl_process = subprocess.run(
                    ["curl", "-LsSf", "https://astral.sh/uv/install.sh"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                install_script_path = "/tmp/uv_install.sh"
                with open(install_script_path, "w") as f:
                    f.write(curl_process.stdout)
                
                os.chmod(install_script_path, 0o755)
                subprocess.run([install_script_path], check=True)
                
                os.remove(install_script_path)
                
                logger.info("Successfully installed uv package manager")
                
                os.environ["PATH"] = f"{os.path.expanduser('~/.cargo/bin')}:{os.environ.get('PATH', '')}"
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install uv: {e}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Unexpected error while installing uv: {e}")
                sys.exit(1)

    def _check_dependency_files_changed(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD@{1}", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            changed_files = result.stdout.strip().split('\n')
            dependency_files = {
                "requirements.txt",
                "uv.lock",
                "pyproject.toml"
            }
            return any(file in changed_files for file in dependency_files)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking dependency file changes: {e}")
            return True

    async def check_for_updates(self) -> bool:
        try:
            subprocess.run(["git", "fetch"], check=True, capture_output=True)
            result = subprocess.run(
                ["git", "status", "-uno"],
                capture_output=True,
                text=True,
                check=True
            )
            return "Your branch is behind" in result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking updates: {e}")
            return False

    def _pull_updates(self) -> bool:
        try:
            subprocess.run(["git", "pull"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error updating: {e}")
            if e.stderr:
                logger.error(f"Git error details: {e.stderr.decode()}")
            return False

    def _install_dependencies(self) -> bool:
        if not self._check_dependency_files_changed():
            logger.info("📦 No changes in dependency files, skipping installation")
            return True

        logger.info("📦 Changes detected in dependency files, updating dependencies...")
        
        try:
            if os.path.exists("pyproject.toml"):
                logger.info("Installing dependencies from pyproject.toml...")
                if os.path.exists("uv.lock"):
                    subprocess.run(["uv", "pip", "sync"], check=True)
                else:
                    subprocess.run(["uv", "pip", "install", "."], check=True)
            elif os.path.exists("uv.lock"):
                logger.info("Installing dependencies from uv.lock...")
                subprocess.run(["uv", "pip", "sync"], check=True)
            elif os.path.exists("requirements.txt"):
                logger.info("Installing dependencies from requirements.txt...")
                subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)
            else:
                logger.warning("No dependency files found")
                return False
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing dependencies: {e}")
            return False

    async def update_and_restart(self) -> None:
        logger.info("🔄 Update detected! Starting update process...")
        
        if not self._pull_updates():
            logger.error("❌ Failed to pull updates")
            return

        if not self._install_dependencies():
            logger.error("❌ Failed to update dependencies")
            return

        logger.info("✅ Update successfully installed! Restarting application...")
        
        new_args = [sys.executable, sys.argv[0], "-a", "1", "--update-restart"]
        os.execv(sys.executable, new_args)

    async def run(self) -> None:
        if not self.is_update_restart:
            await asyncio.sleep(10)
        
        while True:
            try:
                if await self.check_for_updates():
                    await self.update_and_restart()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error during update check: {e}")
                await asyncio.sleep(60)

    def _get_current_remote(self) -> str:
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting current repository: {e}")
            return ""

    def _switch_to_bitbucket(self, current_remote: str) -> None:
        try:
            if "github.com" in current_remote:
                new_remote = current_remote.replace("github.com", "bitbucket.org")
                subprocess.run(
                    ["git", "remote", "set-url", "origin", new_remote],
                    check=True,
                    capture_output=True
                )
                logger.info("🔄 Successfully switched to Bitbucket")
                
                subprocess.run(["git", "fetch"], check=True, capture_output=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error switching to Bitbucket: {e}")

    def _check_and_switch_repository(self) -> None:
        current_remote = self._get_current_remote()
        if current_remote:
            self._switch_to_bitbucket(current_remote)