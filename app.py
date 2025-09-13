from flask import Flask, render_template_string, request, send_file, jsonify
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import json
import time
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mgtu-schedule-downloader-2025'

# Telegram Mini App HTML шаблон
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Расписания СПО МГТУ</title>

    <!-- Telegram WebApp SDK -->
    <script src="https://telegram.org/js/telegram-web-app.js"></script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
        :root {
            /* Telegram Theme Variables */
            --tg-theme-bg-color: var(--tg-theme-bg-color, #ffffff);
            --tg-theme-text-color: var(--tg-theme-text-color, #000000);
            --tg-theme-hint-color: var(--tg-theme-hint-color, #999999);
            --tg-theme-link-color: var(--tg-theme-link-color, #2481cc);
            --tg-theme-button-color: var(--tg-theme-button-color, #2481cc);
            --tg-theme-button-text-color: var(--tg-theme-button-text-color, #ffffff);
            --tg-theme-secondary-bg-color: var(--tg-theme-secondary-bg-color, #f1f1f1);

            /* App Colors */
            --primary-color: var(--tg-theme-button-color, #2563eb);
            --secondary-color: #10b981;
            --success-color: #059669;
            --warning-color: #d97706;
            --danger-color: #dc2626;
            --border-radius: 12px;
            --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--tg-theme-bg-color);
            color: var(--tg-theme-text-color);
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            -webkit-user-select: none;
            user-select: none;
        }

        .container-fluid {
            padding: 8px;
            max-width: 100vw;
        }

        .header-section {
            background: var(--tg-theme-secondary-bg-color);
            border-radius: var(--border-radius);
            padding: 16px;
            margin-bottom: 16px;
            text-align: center;
        }

        .header-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
        }

        .header-subtitle {
            font-size: 14px;
            color: var(--tg-theme-hint-color);
            margin: 4px 0 0 0;
        }

        .content-section {
            background: var(--tg-theme-bg-color);
            border-radius: var(--border-radius);
            padding: 16px;
            margin-bottom: 16px;
        }

        .alert-info {
            background: rgba(37, 99, 235, 0.1);
            border: 1px solid rgba(37, 99, 235, 0.2);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 14px;
            color: var(--tg-theme-text-color);
        }

        .btn-primary {
            background: var(--primary-color);
            border: none;
            border-radius: 8px;
            color: var(--tg-theme-button-text-color);
            font-weight: 500;
            padding: 12px 24px;
            width: 100%;
            font-size: 16px;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .btn-primary:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            transform: none;
        }

        .search-container {
            background: var(--tg-theme-secondary-bg-color);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
        }

        .search-input {
            width: 100%;
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 16px;
            background: var(--tg-theme-bg-color);
            color: var(--tg-theme-text-color);
        }

        .search-input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
        }

        .stats-row {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }

        .stats-card {
            flex: 1;
            background: var(--tg-theme-secondary-bg-color);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }

        .stats-number {
            font-size: 24px;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
        }

        .stats-label {
            font-size: 12px;
            color: var(--tg-theme-hint-color);
            margin: 4px 0 0 0;
        }

        .nav-tabs {
            display: flex;
            background: var(--tg-theme-secondary-bg-color);
            border-radius: 8px;
            padding: 4px;
            margin-bottom: 16px;
        }

        .nav-tab {
            flex: 1;
            background: none;
            border: none;
            border-radius: 6px;
            padding: 8px 4px;
            font-size: 14px;
            font-weight: 500;
            color: var(--tg-theme-hint-color);
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .nav-tab.active {
            background: var(--tg-theme-bg-color);
            color: var(--primary-color);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .file-item {
            background: var(--tg-theme-bg-color);
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            transition: all 0.2s ease;
        }

        .file-item:hover {
            border-color: var(--primary-color);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .file-item.highlighted {
            border-color: var(--warning-color);
            background: rgba(217, 119, 6, 0.05);
        }

        .file-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }

        .file-icon {
            width: 32px;
            height: 32px;
            background: var(--success-color);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 14px;
            margin-right: 12px;
        }

        .file-name {
            flex: 1;
            font-size: 14px;
            font-weight: 500;
            color: var(--tg-theme-text-color);
            line-height: 1.3;
        }

        .file-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .file-meta {
            font-size: 12px;
            color: var(--tg-theme-hint-color);
        }

        .btn-download {
            background: var(--success-color);
            border: none;
            border-radius: 6px;
            color: white;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-download:hover {
            opacity: 0.9;
        }

        .btn-download:disabled {
            opacity: 0.6;
        }

        .department-header {
            background: var(--primary-color);
            color: var(--tg-theme-button-text-color);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 14px;
            font-weight: 600;
        }

        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .progress-bar {
            width: 100%;
            height: 4px;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 8px;
        }

        .progress-fill {
            height: 100%;
            background: var(--success-color);
            border-radius: 2px;
            transition: width 0.3s ease;
            width: 0%;
        }

        .no-results {
            text-align: center;
            padding: 32px 16px;
            color: var(--tg-theme-hint-color);
        }

        .search-highlight {
            background: rgba(217, 119, 6, 0.3);
            padding: 1px 2px;
            border-radius: 2px;
            font-weight: 600;
        }

        .sort-controls {
            background: var(--tg-theme-secondary-bg-color);
            border-radius: 8px;
            padding: 8px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .sort-buttons {
            display: flex;
            gap: 4px;
        }

        .sort-btn {
            background: none;
            border: 1px solid rgba(0, 0, 0, 0.2);
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            color: var(--tg-theme-text-color);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .sort-btn.active {
            background: var(--primary-color);
            color: var(--tg-theme-button-text-color);
            border-color: var(--primary-color);
        }

        .date-badge {
            background: var(--warning-color);
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 500;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .status-message {
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 14px;
        }

        .status-success {
            background: rgba(5, 150, 105, 0.1);
            border: 1px solid rgba(5, 150, 105, 0.2);
            color: var(--success-color);
        }

        .status-error {
            background: rgba(220, 38, 38, 0.1);
            border: 1px solid rgba(220, 38, 38, 0.2);
            color: var(--danger-color);
        }

        /* Telegram-specific adjustments */
        @media (max-width: 480px) {
            .container-fluid {
                padding: 4px;
            }

            .stats-row {
                gap: 4px;
            }

            .file-name {
                font-size: 13px;
            }
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- Заголовок -->
        <div class="header-section">
            <h1 class="header-title">
                <i class="fas fa-file-excel"></i>
                Расписания СПО МГТУ
            </h1>
            <p class="header-subtitle">Скачивание файлов расписаний и замен</p>
        </div>

        <!-- Основной контент -->
        <div class="content-section">
            <!-- Информация -->
            <div class="alert-info">
                <i class="fas fa-info-circle"></i>
                <strong>Источники:</strong> Прямые ссылки на отделения СПО и замены по семестрам
            </div>

            <!-- Кнопка сканирования -->
            <button id="scanBtn" class="btn-primary">
                <i class="fas fa-search"></i>
                Найти файлы расписаний
            </button>

            <!-- Статус -->
            <div id="status" style="display: none;"></div>

            <!-- Поиск -->
            <div id="searchContainer" class="search-container" style="display: none;">
                <input type="text" id="searchInput" class="search-input" 
                       placeholder="Поиск по названию файла...">
                <div style="margin-top: 8px; font-size: 12px; color: var(--tg-theme-hint-color);">
                    Найдено: <span id="searchResults">0</span> файлов
                </div>
            </div>

            <!-- Статистика -->
            <div id="statsContainer" style="display: none;">
                <div class="stats-row">
                    <div class="stats-card">
                        <div class="stats-number" id="semester1Count">0</div>
                        <div class="stats-label">1 семестр</div>
                    </div>
                    <div class="stats-card">
                        <div class="stats-number" id="semester2Count">0</div>
                        <div class="stats-label">2 семестр</div>
                    </div>
                    <div class="stats-card">
                        <div class="stats-number" id="changesCount">0</div>
                        <div class="stats-label">Замены</div>
                    </div>
                </div>
            </div>

            <!-- Вкладки -->
            <div id="tabsContainer" style="display: none;">
                <div class="nav-tabs">
                    <button class="nav-tab active" data-tab="semester1">
                        <i class="fas fa-calendar-alt"></i> 1 семестр
                    </button>
                    <button class="nav-tab" data-tab="semester2">
                        <i class="fas fa-calendar"></i> 2 семестр
                    </button>
                    <button class="nav-tab" data-tab="changes">
                        <i class="fas fa-exchange-alt"></i> Замены
                    </button>
                </div>

                <!-- Содержимое вкладок -->
                <div class="tab-content active" id="semester1Tab">
                    <div id="semester1Files"></div>
                </div>

                <div class="tab-content" id="semester2Tab">
                    <div id="semester2Files"></div>
                </div>

                <div class="tab-content" id="changesTab">
                    <div id="changesSort" class="sort-controls" style="display: none;">
                        <span style="font-size: 12px; font-weight: 500;">Сортировка:</span>
                        <div class="sort-buttons">
                            <button class="sort-btn active" data-sort="newest">Новые</button>
                            <button class="sort-btn" data-sort="oldest">Старые</button>
                            <button class="sort-btn" data-sort="alpha">А-Я</button>
                        </div>
                    </div>
                    <div id="changesFiles"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Telegram WebApp initialization
        let tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();

        // Apply Telegram theme
        document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
        document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
        document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');
        document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f1f1f1');

        // Get user info
        const user = tg.initDataUnsafe.user;
        console.log('Telegram user:', user);

        // App variables
        let allFiles = [];
        let filteredFiles = [];
        let currentTab = 'semester1';

        // Utility functions
        function showAlert(message) {
            if (tg.showAlert) {
                tg.showAlert(message);
            } else {
                alert(message);
            }
        }

        function showConfirm(message, callback) {
            if (tg.showConfirm) {
                tg.showConfirm(message, callback);
            } else {
                callback(confirm(message));
            }
        }

        function extractDateFromFilename(filename) {
            const datePatterns = [
                /(\d{2})\.(\d{2})\.(\d{2,4})/g,
                /(\d{2})-(\d{2})-(\d{2,4})/g,
                /(\d{4})-(\d{2})-(\d{2})/g,
                /(\d{2})_(\d{2})_(\d{2,4})/g
            ];

            for (let pattern of datePatterns) {
                const match = pattern.exec(filename);
                if (match) {
                    let day, month, year;

                    if (pattern.source.includes('(\\d{4})')) {
                        year = parseInt(match[1]);
                        month = parseInt(match[2]) - 1;
                        day = parseInt(match[3]);
                    } else {
                        day = parseInt(match[1]);
                        month = parseInt(match[2]) - 1;
                        year = parseInt(match[3]);

                        if (year < 100) {
                            year += 2000;
                        }
                    }

                    return new Date(year, month, day);
                }
            }

            return new Date();
        }

        function highlightSearchTerm(text, searchTerm) {
            if (!searchTerm) return text;

            const regex = new RegExp(`(${searchTerm})`, 'gi');
            return text.replace(regex, '<span class="search-highlight">$1</span>');
        }

        function performSearch() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();

            if (!searchTerm) {
                filteredFiles = allFiles;
            } else {
                filteredFiles = allFiles.filter(file => 
                    file.name.toLowerCase().includes(searchTerm)
                );
            }

            document.getElementById('searchResults').textContent = filteredFiles.length;
            renderCurrentTab();
        }

        function sortChangesFiles(files, sortOrder) {
            const sortedFiles = [...files];

            switch (sortOrder) {
                case 'newest':
                    return sortedFiles.sort((a, b) => extractDateFromFilename(b.name) - extractDateFromFilename(a.name));
                case 'oldest':
                    return sortedFiles.sort((a, b) => extractDateFromFilename(a.name) - extractDateFromFilename(b.name));
                case 'alpha':
                    return sortedFiles.sort((a, b) => a.name.localeCompare(b.name, 'ru'));
                default:
                    return sortedFiles;
            }
        }

        function renderFiles(files, containerId, searchTerm = '', isChanges = false) {
            const container = document.getElementById(containerId);

            if (files.length === 0) {
                container.innerHTML = `
                    <div class="no-results">
                        <i class="fas fa-search" style="font-size: 32px; margin-bottom: 8px;"></i>
                        <div style="font-size: 14px;">Файлы не найдены</div>
                    </div>
                `;
                return;
            }

            if (isChanges) {
                const sortOrder = document.querySelector('.sort-btn.active').dataset.sort;
                files = sortChangesFiles(files, sortOrder);
                document.getElementById('changesSort').style.display = 'flex';
            }

            // Group files by source
            const groupedFiles = {};
            files.forEach((file, index) => {
                if (!groupedFiles[file.source]) {
                    groupedFiles[file.source] = [];
                }
                groupedFiles[file.source].push({...file, index});
            });

            let html = '';
            Object.keys(groupedFiles).forEach(source => {
                html += `
                    <div class="department-header">
                        <i class="fas fa-folder"></i> ${source}
                        <span style="float: right;">${groupedFiles[source].length}</span>
                    </div>
                `;

                groupedFiles[source].forEach(file => {
                    const isHighlighted = searchTerm && file.name.toLowerCase().includes(searchTerm.toLowerCase());
                    const fileDate = isChanges ? extractDateFromFilename(file.name) : null;

                    html += `
                        <div class="file-item ${isHighlighted ? 'highlighted' : ''}">
                            <div class="file-header">
                                <div class="file-icon">
                                    <i class="fas fa-file-excel"></i>
                                </div>
                                <div class="file-name">${highlightSearchTerm(file.name, searchTerm)}</div>
                            </div>
                            <div class="file-actions">
                                <div class="file-meta">
                                    <i class="fas fa-file"></i> Excel
                                    ${fileDate ? `<span class="date-badge">${fileDate.toLocaleDateString('ru-RU')}</span>` : ''}
                                </div>
                                <button class="btn-download" onclick="downloadFile(${file.globalIndex})">
                                    <i class="fas fa-download"></i> Скачать
                                </button>
                            </div>
                            <div class="progress-bar" id="progress_${file.globalIndex}" style="display: none;">
                                <div class="progress-fill"></div>
                            </div>
                        </div>
                    `;
                });
            });

            container.innerHTML = html;
        }

        function renderCurrentTab() {
            const searchTerm = document.getElementById('searchInput').value;

            switch (currentTab) {
                case 'semester1':
                    renderFiles(filteredFiles.filter(f => f.category === 'semester1'), 'semester1Files', searchTerm);
                    break;
                case 'semester2':
                    renderFiles(filteredFiles.filter(f => f.category === 'semester2'), 'semester2Files', searchTerm);
                    break;
                case 'changes':
                    renderFiles(filteredFiles.filter(f => f.category === 'changes'), 'changesFiles', searchTerm, true);
                    break;
            }
        }

        function downloadFile(fileIndex) {
            const progressBar = document.getElementById(`progress_${fileIndex}`);
            const progressFill = progressBar.querySelector('.progress-fill');
            const button = event.target;

            button.disabled = true;
            button.innerHTML = '<div class="loading-spinner"></div>';
            progressBar.style.display = 'block';

            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 30;
                if (progress > 90) progress = 90;
                progressFill.style.width = progress + '%';
            }, 200);

            // Download file using fetch and blob
            fetch(`/download/${fileIndex}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    // Get filename from response headers or use default
                    const contentDisposition = response.headers.get('Content-Disposition');
                    let filename = 'schedule.xlsx';
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                        if (filenameMatch) {
                            filename = filenameMatch[1];
                        }
                    }
                    
                    return response.blob().then(blob => ({ blob, filename }));
                })
                .then(({ blob, filename }) => {
                    // Create download link
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);

                    // Complete progress
                    clearInterval(progressInterval);
                    progressFill.style.width = '100%';

                    setTimeout(() => {
                        button.disabled = false;
                        button.innerHTML = '<i class="fas fa-download"></i> Скачать';
                        progressBar.style.display = 'none';
                        progressFill.style.width = '0%';

                        showAlert('Файл загружен!');
                    }, 1000);
                })
                .catch(error => {
                    console.error('Download error:', error);
                    clearInterval(progressInterval);
                    
                    // Fallback: try direct download
                    try {
                        window.open(`/download/${fileIndex}`, '_blank');
                        
                        setTimeout(() => {
                            button.disabled = false;
                            button.innerHTML = '<i class="fas fa-download"></i> Скачать';
                            progressBar.style.display = 'none';
                            progressFill.style.width = '0%';
                            showAlert('Файл загружен!');
                        }, 1000);
                    } catch (fallbackError) {
                        console.error('Fallback download error:', fallbackError);
                        button.disabled = false;
                        button.innerHTML = '<i class="fas fa-download"></i> Скачать';
                        progressBar.style.display = 'none';
                        progressFill.style.width = '0%';
                        showAlert('Ошибка при скачивании файла. Попробуйте еще раз.');
                    }
                });
        }

        // Event listeners
        document.getElementById('searchInput').addEventListener('input', performSearch);

        // Tab switching
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', function() {
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

                this.classList.add('active');
                currentTab = this.dataset.tab;
                document.getElementById(currentTab + 'Tab').classList.add('active');

                renderCurrentTab();
            });
        });

        // Sort controls
        document.querySelectorAll('.sort-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                if (currentTab === 'changes') {
                    renderCurrentTab();
                }
            });
        });

        // Main scan button
        document.getElementById('scanBtn').addEventListener('click', function() {
            const btn = this;
            const status = document.getElementById('status');

            btn.disabled = true;
            btn.innerHTML = '<div class="loading-spinner"></div> Поиск файлов...';

            fetch('/scan')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        status.className = 'status-message status-success';
                        status.innerHTML = `
                            <i class="fas fa-check-circle"></i>
                            Найдено файлов: <strong>${data.files.length}</strong>
                        `;
                        status.style.display = 'block';

                        allFiles = data.files;
                        filteredFiles = data.files;

                        allFiles.forEach((file, index) => {
                            file.globalIndex = index;
                        });

                        const semester1Files = allFiles.filter(file => file.category === 'semester1');
                        const semester2Files = allFiles.filter(file => file.category === 'semester2');
                        const changesFiles = allFiles.filter(file => file.category === 'changes');

                        document.getElementById('semester1Count').textContent = semester1Files.length;
                        document.getElementById('semester2Count').textContent = semester2Files.length;
                        document.getElementById('changesCount').textContent = changesFiles.length;
                        document.getElementById('searchResults').textContent = allFiles.length;

                        renderCurrentTab();

                        document.getElementById('tabsContainer').style.display = 'block';
                        document.getElementById('statsContainer').style.display = 'block';
                        document.getElementById('searchContainer').style.display = 'block';

                        showAlert(`Найдено ${data.files.length} файлов!`);

                    } else {
                        status.className = 'status-message status-error';
                        status.innerHTML = `
                            <i class="fas fa-exclamation-triangle"></i>
                            Ошибка при сканировании
                        `;
                        status.style.display = 'block';
                        showAlert('Ошибка при сканировании файлов');
                    }
                })
                .catch(error => {
                    status.className = 'status-message status-error';
                    status.innerHTML = `
                        <i class="fas fa-exclamation-triangle"></i>
                        Ошибка сети
                    `;
                    status.style.display = 'block';
                    showAlert('Ошибка подключения к серверу');
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-search"></i> Найти файлы расписаний';
                });
        });

        // Send data to bot when app closes
        tg.onEvent('mainButtonClicked', function() {
            tg.sendData(JSON.stringify({
                action: 'scan_completed',
                files_count: allFiles.length,
                user_id: user ? user.id : null
            }));
        });
    </script>
</body>
</html>
'''


class MGTUScheduleScraper:
    def __init__(self):
        self.base_url = "https://newlms.magtu.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        self.sources = {
            'semester1': [
                {
                    'name': 'Отделение №1 "ОБЩЕОБРАЗОВАТЕЛЬНАЯ ПОДГОТОВКА"',
                    'url': 'https://newlms.magtu.ru/mod/folder/view.php?id=1584679'
                },
                {
                    'name': 'Отделение №2 "ИНФОРМАЦИОННЫХ ТЕХНОЛОГИЙ И ТРАНСПОРТА"',
                    'url': 'https://newlms.magtu.ru/mod/folder/view.php?id=1584691'
                },
                {
                    'name': 'Отделение №3 "СТРОИТЕЛЬСТВА, ЭКОНОМИКИ И СФЕРЫ ОБСЛУЖИВАНИЯ"',
                    'url': 'https://newlms.magtu.ru/mod/folder/view.php?id=1584686'
                }
            ],
            'semester1_changes': [
                {
                    'name': 'Замены 1 семестра',
                    'url': 'https://newlms.magtu.ru/mod/folder/view.php?id=219250'
                }
            ],
            'semester2': [
                {
                    'name': 'Отделение №1 "ОБЩЕОБРАЗОВАТЕЛЬНАЯ ПОДГОТОВКА" (2 семестр)',
                    'url': 'https://newlms.magtu.ru/mod/folder/view.php?id=1223698'
                },
                {
                    'name': 'Отделение №2 "ИНФОРМАЦИОННЫХ ТЕХНОЛОГИЙ И ТРАНСПОРТА" (2 семестр)',
                    'url': 'https://newlms.magtu.ru/mod/folder/view.php?id=1584699'
                },
                {
                    'name': 'Отделение №3 "СТРОИТЕЛЬСТВА, ЭКОНОМИКИ И СФЕРЫ ОБСЛУЖИВАНИЯ" (2 семестр)',
                    'url': 'https://newlms.magtu.ru/mod/folder/view.php?id=1584701'
                }
            ],
            'semester2_changes': [
                {
                    'name': 'Замены 2 семестра',
                    'url': 'https://newlms.magtu.ru/mod/folder/view.php?id=1223702'
                }
            ]
        }

    def _is_xlsx_file(self, href, link_text):
        url_lower = href.lower()
        text_lower = link_text.lower()

        return (url_lower.endswith('.xlsx') or '.xlsx' in url_lower or
                text_lower.endswith('.xlsx') or '.xlsx' in text_lower)

    def get_files_from_source(self, source_url, source_name, category):
        try:
            print(f"🔍 Сканирование: {source_name}")
            response = self.session.get(source_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            files = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True)

                if not link_text:
                    continue

                if self._is_xlsx_file(href, link_text):
                    full_url = urljoin(self.base_url, href)

                    files.append({
                        'url': full_url,
                        'name': link_text,
                        'type': '.xlsx',
                        'source': source_name,
                        'category': category,
                        'found_at': datetime.now().isoformat()
                    })
                    print(f"  ✅ Найден .xlsx файл: {link_text}")

            print(f"📊 Найдено файлов .xlsx в {source_name}: {len(files)}")
            return files

        except Exception as e:
            print(f"❌ Ошибка при получении файлов из {source_name}: {e}")
            return []

    def get_all_files(self):
        print("🚀 Начинаем сканирование всех источников...")
        all_files = []
        all_sources = []

        for category, sources in self.sources.items():
            for source in sources:
                if category.endswith('_changes'):
                    cat = 'changes'
                elif '1' in category:
                    cat = 'semester1'
                else:
                    cat = 'semester2'

                source_files = self.get_files_from_source(source['url'], source['name'], cat)
                all_files.extend(source_files)
                all_sources.append(source['name'])

        # Remove duplicates
        unique_files = []
        seen_urls = set()
        for file_info in all_files:
            if file_info['url'] not in seen_urls:
                seen_urls.add(file_info['url'])
                unique_files.append(file_info)

        category_stats = {'semester1': 0, 'semester2': 0, 'changes': 0}
        for file_info in unique_files:
            category_stats[file_info['category']] += 1

        print(f"\n📈 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"📁 Всего найдено уникальных файлов .xlsx: {len(unique_files)}")
        print(f"📅 1 семестр: {category_stats['semester1']} файлов")
        print(f"📅 2 семестр: {category_stats['semester2']} файлов")
        print(f"🔄 Замены: {category_stats['changes']} файлов")

        return unique_files, all_sources

    def download_file(self, file_url, filename, download_dir="downloads"):
        try:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            if not safe_filename.endswith('.xlsx'):
                safe_filename += '.xlsx'

            filepath = os.path.join(download_dir, safe_filename)

            print(f"⬇️ Скачивание файла: {safe_filename}")
            response = self.session.get(file_url, stream=True, timeout=60)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"✅ Файл успешно скачан: {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ Ошибка при скачивании файла {filename}: {e}")
            return None


# Global variables
found_files = []
found_sources = []


@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)


@app.route('/scan')
def scan_files():
    global found_files, found_sources
    try:
        scraper = MGTUScheduleScraper()
        found_files, found_sources = scraper.get_all_files()

        return jsonify({
            'status': 'success',
            'files': found_files,
            'sources': found_sources,
            'count': len(found_files),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"❌ Ошибка в /scan: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/download/<int:file_index>')
def download_file(file_index):
    global found_files

    if file_index >= len(found_files) or file_index < 0:
        return "Файл не найден", 404

    file_info = found_files[file_index]
    scraper = MGTUScheduleScraper()

    category_prefix = {
        'semester1': '1сем_',
        'semester2': '2сем_',
        'changes': 'Замены_'
    }.get(file_info['category'], '')

    date_prefix = datetime.now().strftime('%Y%m%d_')
    source_prefix = re.sub(r'[<>:"/\\|?*]', '_', file_info['source'])[:20]
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', file_info['name'])

    filename = f"{date_prefix}{category_prefix}{source_prefix}_{safe_name}.xlsx"

    local_path = scraper.download_file(file_info['url'], filename)

    if local_path and os.path.exists(local_path):
        return send_file(
            local_path, 
            as_attachment=True, 
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        return "Ошибка при скачивании файла", 500


if __name__ == '__main__':
    print("🚀 Запуск Telegram Mini App для расписаний СПО МГТУ")
    print("📱 Оптимизировано для Telegram WebApp")
    print("🌐 Откройте http://localhost:5000 в браузере")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
