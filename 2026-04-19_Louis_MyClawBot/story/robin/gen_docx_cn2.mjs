import { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
         AlignmentType, WidthType, ShadingType, VerticalAlign, Header, Footer, PageBreak } from 'docx';
import fs from 'fs';

// 原始中文版
const orig = JSON.parse(fs.readFileSync('storyboard.json', 'utf-8'));
// v2 增强结构
const v2 = JSON.parse(fs.readFileSync('storyboard_v2.json', 'utf-8'));

// 建立 v2 shot 索引
const v2map = {};
v2.shots.forEach(s => { v2map[s.shot_index] = s; });

// 合并
const merged = { ...orig, character_tracking: v2.character_tracking, scenes: v2.scenes };
merged.shots = orig.shots.map(shot => {
  const v = v2map[shot.shot_index];
  return {
    ...shot,
    shot_type: v ? v.shot_type : shot.scene,
    camera_detail: v ? v.camera_detail : {},
    position: v ? v.position : {},
    ref_images_logic: v ? v.ref_images_logic : '',
    narrative_function: v ? v.narrative_function : '',
    emotion_tone: v ? v.emotion_tone : '',
    audio_cue: v ? v.audio_cue : '',
  };
});

const storyboard = merged;

const C = { title: '1E2761', scene_col: '065A82', header_bg: '1E2761', white: 'FFFFFF', row_alt: 'F0F4F8', body: '36454F', gold: 'B85042' };

function bold(text, size = 20, color = C.body) { return new TextRun({ text, bold: true, size, color }); }
function run(text, size = 18, color = C.body) { return new TextRun({ text, size, color }); }
function spacer() { return new Paragraph({ children: [new TextRun('')], spacing: { before: 60, after: 60 } }); }
function pageBreak() { return new Paragraph({ children: [new PageBreak()] }); }

const shotTypeCN = {
  establishing: '定场镜头', action: '动作镜头', reaction: '反应镜头',
  insert: '插入特写', cutaway: '游离镜头'
};
const narrativeCN = {
  establishing: '建置', tension_build: '张力积累', climax_build: '高潮铺垫',
  climax: '高潮', tension_release: '张力释放', transition: '转场'
};

function makeShotTable(shots) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: ['#', '时间', '场景', '镜头类型', '叙事功能', '摄像机', 'Prompt（中文）', '参考图', '音效/情绪'].map(h => new TableCell({
      width: { size: 1000, type: WidthType.DXA },
      shading: { fill: C.header_bg, type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: C.white, size: 17 })] })]
    }))
  });

  const rows = [];
  shots.forEach((shot, idx) => {
    const bg = idx % 2 === 0 ? C.white : C.row_alt;
    const cd = shot.camera_detail || {};
    const camStr = `${cd.movement || ''} / ${cd.angle || ''} / ${cd.focal_length || ''} / ${cd.depth_of_field || ''}`;
    const refStr = shot.ref_images && shot.ref_images.length > 0
      ? shot.ref_images.map(r => r.replace('refs/', '')).join(', ') : '—';
    const typeCN = shotTypeCN[shot.shot_type] || shot.shot_type || '';
    const narCN = narrativeCN[shot.narrative_function] || shot.narrative_function || '';
    const audioEmo = `[${shot.emotion_tone || ''}] ${shot.audio_cue || ''}`;
    const timeStr = (shot.time || '').replace('00:', '');
    // 取中文 prompt 前 120 字
    const promptShort = (shot.prompt || '').length > 120
      ? (shot.prompt || '').substring(0, 120) + '...'
      : (shot.prompt || '');

    rows.push(new TableRow({
      children: [
        new TableCell({ width: { size: 350, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [bold(`${shot.shot_index}`, 18, C.title)] })] }),
        new TableCell({ width: { size: 650, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [run(timeStr, 16)] })] }),
        new TableCell({ width: { size: 550, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [run(shot.scene || '', 16)] })] }),
        new TableCell({ width: { size: 700, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [run(typeCN, 16)] })] }),
        new TableCell({ width: { size: 650, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [run(narCN, 15)] })] }),
        new TableCell({ width: { size: 850, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [run(camStr, 14)] })] }),
        new TableCell({ width: { size: 2200, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [run(promptShort, 14)] })] }),
        new TableCell({ width: { size: 900, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [run(refStr, 13)] })] }),
        new TableCell({ width: { size: 950, type: WidthType.DXA }, shading: { fill: bg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.TOP, children: [new Paragraph({ children: [run(audioEmo.substring(0, 55) + (audioEmo.length > 55 ? '...' : ''), 13)] })] }),
      ]
    }));
  });

  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: [headerRow, ...rows] });
}

function makeCharacterTable(tracking) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: ['角色名', '外观特征', '出场镜头', '最后一帧'].map(h => new TableCell({
      shading: { fill: C.scene_col, type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: C.white, size: 18 })] })]
    }))
  });
  const charRows = Object.entries(tracking).map(([key, c]) => {
    const appearance = c.hair ? `发型: ${c.hair} | 服装: ${c.clothing}` : (c.body || c.vehicle || '—');
    const shotsStr = c.shots ? c.shots.join(', ') : '—';
    return new TableRow({
      children: [
        new TableCell({ children: [new Paragraph({ children: [bold(c.name || key, 17)] })] }),
        new TableCell({ children: [new Paragraph({ children: [run(appearance, 15)] })] }),
        new TableCell({ children: [new Paragraph({ children: [run(shotsStr, 17)] })] }),
        new TableCell({ children: [new Paragraph({ children: [run(c.last_frame || '—', 15)] })] }),
      ]
    });
  });
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: [headerRow, ...charRows] });
}

function makeSceneTable(scenes) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: ['场景', '时间段', '地点', '灯光', '氛围'].map(h => new TableCell({
      shading: { fill: C.gold, type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: C.white, size: 18 })] })]
    }))
  });
  const scRows = scenes.map(s => new TableRow({
    children: [
      new TableCell({ children: [new Paragraph({ children: [bold(s.name, 17)] })] }),
      new TableCell({ children: [new Paragraph({ children: [run(s.time, 17)] })] }),
      new TableCell({ children: [new Paragraph({ children: [run(s.location, 17)] })] }),
      new TableCell({ children: [new Paragraph({ children: [run(s.lighting, 17)] })] }),
      new TableCell({ children: [new Paragraph({ children: [run(s.atmosphere, 17)] })] }),
    ]
  }));
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: [headerRow, ...scRows] });
}

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 15840, height: 12240 },
        margin: { top: 720, right: 720, bottom: 720, left: 720 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({ children: [new TextRun({ text: `${storyboard.project} — ${storyboard.episode}`, bold: true, size: 18, color: C.scene_col })] })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: 'Generated by 小志 × OpenClaw', size: 16, color: '888888' })] })]
      })
    },
    children: [
      new Paragraph({ children: [new TextRun({ text: storyboard.project, bold: true, size: 56, color: C.title })], spacing: { before: 0, after: 120 } }),
      new Paragraph({ children: [new TextRun({ text: storyboard.episode, size: 32, color: C.scene_col })], spacing: { before: 0, after: 240 } }),

      new Table({
        width: { size: 60, type: WidthType.PERCENTAGE },
        rows: [new TableRow({ children: [
          new TableCell({ children: [new Paragraph({ children: [bold('模型: ', 18), run(storyboard.model, 18)] })] }),
          new TableCell({ children: [new Paragraph({ children: [bold('分辨率: ', 18), run(storyboard.resolution, 18)] })] }),
          new TableCell({ children: [new Paragraph({ children: [bold('帧率: ', 18), run(`${storyboard.fps} fps`, 18)] })] }),
          new TableCell({ children: [new Paragraph({ children: [bold('总时长: ', 18), run(`${storyboard.total_duration}秒`, 18)] })] }),
        ]})]
      }),
      spacer(),

      new Paragraph({ children: [new TextRun({ text: '角色追踪', bold: true, size: 28, color: C.title })], spacing: { before: 360, after: 120 } }),
      makeCharacterTable(storyboard.character_tracking),
      spacer(),

      new Paragraph({ children: [new TextRun({ text: '场景概览', bold: true, size: 28, color: C.title })], spacing: { before: 360, after: 120 } }),
      makeSceneTable(storyboard.scenes),
      spacer(),

      pageBreak(),

      new Paragraph({ children: [new TextRun({ text: '镜头详解', bold: true, size: 28, color: C.title })], spacing: { before: 0, after: 120 } }),
      new Paragraph({ children: [new TextRun({ text: `共 ${storyboard.shots.length} 个镜头 | 完整中文 Prompt`, size: 18, color: '666666' })], spacing: { before: 0, after: 200 } }),
      makeShotTable(storyboard.shots),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('storyboard_cn.docx', buf);
  console.log('Done: storyboard_cn.docx');
});
