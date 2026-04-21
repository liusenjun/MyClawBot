const d = require('./node_modules/docx');
const keys = Object.keys(d).filter(k => k.toLowerCase().includes('page'));
console.log(keys.join('\n'));
