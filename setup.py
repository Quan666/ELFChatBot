#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="elfchatbot",
    version="0.0.1",
    author="Quan666",
    author_email="i@oy.mk",
    description="闲聊QQ机器人，也就是人工智障",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Quan666/ELFChatBot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
