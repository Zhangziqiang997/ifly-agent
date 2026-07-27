import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');

test('home keeps only the upload, risk and report overview panels', () => {
  const html = read('index.html');
  assert.doesNotMatch(html, /核心工作入口/);
  assert.doesNotMatch(html, /AI研判结果/);
  assert.doesNotMatch(html, /讯飞AI产品能力/);
  assert.doesNotMatch(html, /id=["']work-list["']/);
  assert.doesNotMatch(html, /id=["']assessment-body["']/);
  assert.doesNotMatch(html, /id=["']capability-list["']/);
});

test('homepage script does not render removed lower sections', () => {
  const app = read('app.js');
  assert.doesNotMatch(app, /work-list|assessment-body|capability-list/);
  assert.doesNotMatch(app, /生成质疑话术|查看参数知识库/);
});
