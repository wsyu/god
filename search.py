#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
File Name ：search.py
date ： 2022/11/22
time ： 16:44
Author ： wsy
desc ：
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.baidu.com")
        await page.screenshot(path=f"screenshot.png")
        print(await page.title())
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
