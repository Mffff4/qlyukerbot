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

    def _check_requirements_changed(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD@{1}", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            changed_files = result.stdout.strip().split('\n')
            return "requirements.txt" in changed_files
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking requirements changes: {e}")
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

    def _install_requirements(self) -> bool:
        try:
            if not self._check_requirements_changed():
                logger.info("📦 No changes in requirements.txt, skipping dependency installation")
                return True
                
            logger.info("📦 Changes detected in requirements.txt, updating dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing dependencies: {e}")
            return False

    async def update_and_restart(self) -> None:
        logger.info("🔄 Update detected! Starting update process...")
        
        if not self._pull_updates():
            logger.error("❌ Failed to pull updates")
            return

        if not self._install_requirements():
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