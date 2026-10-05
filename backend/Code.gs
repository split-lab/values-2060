/**
 * MIS20070 - Values 2060 survey backend (Google Apps Script, bound to the responses Sheet)
 * doPost: saves one response, blocks duplicates. doGet: returns all points + count.
 * setup(): run ONCE from the editor - creates the 'responses' tab and headers, and triggers Google's permission prompt.
 */
const SHEET = 'responses';
const HEADERS = ['timestamp','respondent_id','today_equality','today_belonging','today_purpose',
                 'f2060_equality','f2060_belonging','f2060_purpose','user_agent'];

function setup() {
  const ss = SpreadsheetApp.getActive();
  let sh = ss.getSheetByName(SHEET);
  if (!sh) { sh = ss.getSheets()[0]; sh.setName(SHEET); }
  sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold');
  sh.setFrozenRows(1);
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const d = JSON.parse(e.postData.contents);
    const sh = SpreadsheetApp.getActive().getSheetByName(SHEET);
    const ok = p => p && [p.e, p.b, p.p].every(n => typeof n === 'number' && n >= 0 && n <= 100)
                      && Math.round(p.e + p.b + p.p) === 100;
    if (!d.respondent_id || !ok(d.t) || !ok(d.f)) return out({ ok: false, reason: 'invalid' });
    const last = sh.getLastRow();
    if (last > 1) {
      const ids = sh.getRange(2, 2, last - 1, 1).getValues().flat();
      if (ids.indexOf(d.respondent_id) !== -1) return out({ ok: false, reason: 'duplicate' });
    }
    sh.appendRow([new Date(), d.respondent_id, d.t.e, d.t.b, d.t.p, d.f.e, d.f.b, d.f.p,
                  String(d.ua || '').slice(0, 180)]);
    return out({ ok: true, n: sh.getLastRow() - 1 });
  } catch (err) {
    return out({ ok: false, reason: 'error' });
  } finally {
    lock.releaseLock();
  }
}

function doGet() {
  const sh = SpreadsheetApp.getActive().getSheetByName(SHEET);
  const last = sh.getLastRow();
  const points = last > 1 ? sh.getRange(2, 3, last - 1, 6).getValues() : [];
  return out({ n: points.length, points: points });
}

function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
