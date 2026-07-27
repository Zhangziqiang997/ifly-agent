import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function read(file) {
  return fs.readFileSync(path.join(root, file), 'utf8');
}

test('all app pages use the shared sidebar placeholder and scripts', () => {
  const pages = [
    ['index.html', 'home'],
    ['knowledge-base.html', 'knowledge'],
    ['report.html', 'report'],
  ];

  for (const [file, page] of pages) {
    const html = read(file);
    assert.match(html, new RegExp(`<aside[^>]*data-sidebar[^>]*data-page="${page}"`));
    assert.match(html, /sidebar-config\.js/);
    assert.match(html, /sidebar\.js/);
  }
});

test('sidebar configuration keeps the complete menu and implemented routes', () => {
  const config = read('sidebar-config.js');
  for (const label of ['业务中心', '智能分析', '产品与知识', '项目总览', 'AI分析报告', '参数知识库']) {
    assert.ok(config.includes(label), `missing menu label: ${label}`);
  }
  assert.match(config, /index\.html/);
  assert.match(config, /knowledge-base\.html/);
  assert.match(config, /report\.html/);
});

test('homepage no longer renders a second sidebar from app.js', () => {
  assert.doesNotMatch(read('app.js'), /side-nav|nav\.innerHTML/);
});

test('shared sidebar preserves the homepage typography standard', () => {
  const css = read('sidebar.css');
  assert.match(css, /\.sidebar \.brand strong\{[^}]*font-size:19px/);
  assert.match(css, /\.sidebar \.group-title\{[^}]*font-size:16px/);
  assert.match(css, /\.sidebar nav a\{[^}]*font-size:15px/);
  assert.match(css, /\.sidebar nav a\{[^}]*font-weight:600/);
});

test('page styles do not retain sidebar selectors', () => {
  for (const file of ['styles.css', 'kb-light.css', 'report-light.css']) {
    assert.doesNotMatch(read(file), /\.sidebar|\.brand|\.business-label|\.business-select|\.sidebar-collapse|\.nav-ico/);
  }
});
