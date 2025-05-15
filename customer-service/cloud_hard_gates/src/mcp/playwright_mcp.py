from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page

class PlaywrightMCP:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def initialize(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def navigate(self, url: str):
        if not self.page:
            await self.initialize()
        await self.page.goto(url)

    async def get_content(self, selector: str) -> str:
        if not self.page:
            raise Exception("Page not initialized")
        element = await self.page.wait_for_selector(selector)
        return await element.text_content()

    async def click(self, selector: str):
        if not self.page:
            raise Exception("Page not initialized")
        await self.page.click(selector)

    async def type_text(self, selector: str, text: str):
        if not self.page:
            raise Exception("Page not initialized")
        await self.page.fill(selector, text)

    async def execute_script(self, script: str) -> Any:
        if not self.page:
            raise Exception("Page not initialized")
        return await self.page.evaluate(script)

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop() 