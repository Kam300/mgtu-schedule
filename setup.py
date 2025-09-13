from setuptools import setup, find_packages

setup(
    name="mgtu-schedule",
    version="1.0.0",
    description="Telegram Mini App для скачивания расписаний СПО МГТУ",
    author="MGTU Schedule Team",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "gunicorn==21.2.0",
        "python-telegram-bot==20.7",
    ],
    python_requires=">=3.8",
)
