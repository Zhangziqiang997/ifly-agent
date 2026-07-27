import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const root = new URL('../', import.meta.url);
const indexHtml = await readFile(new URL('index.html', root), 'utf8');
const appJs = await readFile(new URL('app.js', root), 'utf8');

test('home exposes a PDF-only file input for the knowledge-base upload flow', () => {
  assert.match(indexHtml, /<input[^>]+type=["']file["'][^>]+accept=["']\.pdf,application\/pdf["'][^>]*>/i);
});

test('home exposes a dedicated AI analysis button with an observable status region', () => {
  assert.match(indexHtml, /<button(?=[^>]*\bid=["']analysis-button["'])(?=[^>]*\btype=["']button["'])[^>]*>/i);
  assert.match(indexHtml, /id=["']analysis-status["'][^>]+aria-live=["']polite["']/i);
  assert.match(appJs, /analysis-button/);
});

test('report entry starts disabled and only targets the report page after analysis', () => {
  assert.match(indexHtml, /<button[^>]+id=["']report-button["'][^>]+disabled[^>]*>/i);
  assert.match(appJs, /report\.html/);
});

test('analysis completion re-enables the button for a subsequent run', () => {
  assert.match(appJs, /analysisButton\.disabled\s*=\s*false/);
});

test('a new PDF upload cancels the previous parse completion callback', () => {
  assert.match(appJs, /clearTimeout\(uploadTimer\)/);
  assert.match(appJs, /uploadTimer\s*=\s*window\.setTimeout/);
});

test('a new analysis run immediately returns the report to its disabled analysing state', () => {
  assert.match(appJs, /analysisButton\.addEventListener\('click',[\s\S]*?reportButton\.disabled\s*=\s*true/);
  assert.match(appJs, /reportState\.textContent\s*=\s*'AI正在分析'/);
});

test('every file-input change cancels parsing before reading the selected file', () => {
  assert.match(appJs, /pdfInput\.addEventListener\('change', \(\) => \{\s*clearTimeout\(uploadTimer\);\s*const \[file\]/);
});

test('empty or invalid file choices restore the initial upload UI', () => {
  assert.match(appJs, /function resetUploadUi\(\)[\s\S]*fileName\.textContent\s*=\s*'暂未选择 PDF 文件'/);
  assert.match(appJs, /function resetUploadUi\(\)[\s\S]*uploadStatus\.textContent\s*=\s*'选择文件后将自动解析'/);
});

test('upload UI reset restores the knowledge-base total to its initial value', () => {
  assert.match(appJs, /function resetUploadUi\(\)[\s\S]*knowledgeTotal\.textContent\s*=\s*'99'/);
});
