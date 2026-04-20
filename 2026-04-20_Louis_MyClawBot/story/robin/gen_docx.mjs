import { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
         AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType,
         VerticalAlign, Header, Footer, PageBreak, PageNumberElement } from 'docx';
import fs from 'fs';

const storyboard = JSON.parse(fs.readFileSync('storyboard_v2.json', 'utf-8'));

// Color palette
const C = {
  title: '1E2761',       // midnight navy
  scene: '065A82',       // deep blue
  shot_hd: '2C5F2D',     // forest green
  gold: 'B85042',        // terracotta accent
  light: 'F5F5F5',       // off-white bg
  mid: 'ECE2D0',        // cream
  body: '36454F',       // charcoal
  white: 'FFFFFF',
  header_bg: '1E2761',
  row_alt: 'F0F4F8',
};

function bold(text, size = 20, color = C.body) {
  return new TextRun({ text, bold: true, size, color });
}
function run(text, size = 18, color = C.body) {
  return new TextRun({ text, size });
}
function heading(text, level) {
  return new Paragraph({ text, heading: level, spacing: { before: 240, after: 120 } });
}
function spacer() {
  return new Paragraph({ children: [new TextRun('')], spacing: { before: 60, after: 60 } });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// Build shot rows (table)
function makeShotTable(shots) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      new TableCell({
        width: { size: 500, type: WidthType.DXA },
        shading: { fill: C.header_bg, type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text: '#', bold: true, color: C.white, size: 18 })] })]
      }),
      new TableCell({
        width: { size: 800, type: WidthType.DXA },
        shading: { fill: C.header_bg, type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text: 'Time', bold: true, color: C.white, size: 18 })] })]
      }),
      new TableCell({
        width: { size: 700, type: WidthType.DXA },
        shading: { fill: C.header_bg, type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text: 'Scene', bold: true, color: C.white, size: 18 })] })]
      }),
      new TableCell({
        width: { size: 800, type: WidthType.DXA },
        shading: { fill: C.header_bg, type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text: 'Shot Type', bold: true, color: C.white, size: 18 })] })]
      }),
      new TableCell({
        width: { size: 1000, type: WidthType.DXA },
        shading: { fill: C.header_bg, type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text: 'Camera', bold: true, color: C.white, size: 18 })] })]
      }),
      new TableCell({
        width: { size: 3000, type: WidthType.DXA },
        shading: { fill: C.header_bg, type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text: 'Prompt', bold: true, color: C.white, size: 18 })] })]
      }),
      new TableCell({
        width: { size: 1000, type: WidthType.DXA },
        shading: { fill: C.header_bg, type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text: 'Ref Images', bold: true, color: C.white, size: 18 })] })]
      }),
      new TableCell({
        width: { size: 1000, type: WidthType.DXA },
        shading: { fill: C.header_bg, type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text: 'Audio / Emotion', bold: true, color: C.white, size: 18 })] })]
      }),
    ]
  });

  const rows = [];
  shots.forEach((shot, idx) => {
    const bg = idx % 2 === 0 ? C.white : C.row_alt;
    const cd = shot.camera_detail;
    const camStr = `${cd.movement} / ${cd.angle} / ${cd.focal_length} / ${cd.depth_of_field}`;
    const refStr = shot.ref_images.length > 0 ? shot.ref_images.join(', ') : '—';
    const audioEmo = `${shot.emotion_tone} | ${shot.audio_cue}`;
    const timeStr = shot.time.replace('00:', '');

    rows.push(new TableRow({
      children: [
        new TableCell({
          width: { size: 500, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ children: [bold(`${shot.shot_index}`, 18, C.title)] })]
        }),
        new TableCell({
          width: { size: 800, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ children: [run(timeStr, 17)] })]
        }),
        new TableCell({
          width: { size: 700, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ children: [run(shot.scene, 17)] })]
        }),
        new TableCell({
          width: { size: 800, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ children: [run(shot.shot_type, 17)] })]
        }),
        new TableCell({
          width: { size: 1000, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ children: [run(camStr, 16)] })]
        }),
        new TableCell({
          width: { size: 3000, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ children: [run(shot.prompt.substring(0, 200) + (shot.prompt.length > 200 ? '...' : ''), 16)] })]
        }),
        new TableCell({
          width: { size: 1000, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ children: [run(refStr, 15)] })]
        }),
        new TableCell({
          width: { size: 1000, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({ children: [run(audioEmo.substring(0, 80) + (audioEmo.length > 80 ? '...' : ''), 15)] })]
        }),
      ]
    }));
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [headerRow, ...rows],
  });
}

// Build character tracking table
function makeCharacterTable(tracking) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: ['Name', 'Appearance', 'Shots', 'Last Frame'].map(h => new TableCell({
      shading: { fill: C.scene, type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: C.white, size: 18 })] })]
    }))
  });
  const charRows = Object.entries(tracking).map(([key, c]) => {
    const appearance = c.hair ? `${c.hair} | ${c.clothing}` : (c.body || c.vehicle || '—');
    const shotsStr = c.shots ? c.shots.join(', ') : '—';
    return new TableRow({
      children: [
        new TableCell({ children: [new Paragraph({ children: [bold(c.name || key, 17)] })] }),
        new TableCell({ children: [new Paragraph({ children: [run(appearance, 17)] })] }),
        new TableCell({ children: [new Paragraph({ children: [run(shotsStr, 17)] })] }),
        new TableCell({ children: [new Paragraph({ children: [run(c.last_frame || '—', 17)] })] }),
      ]
    });
  });
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [headerRow, ...charRows],
  });
}

// Build scene overview table
function makeSceneTable(scenes) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: ['Scene', 'Time', 'Location', 'Lighting', 'Atmosphere'].map(h => new TableCell({
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
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [headerRow, ...scRows],
  });
}

// Main document
const doc = new Document({
  styles: {
    paragraphStyles: [
      {
        id: 'Title',
        name: 'Title',
        basedOn: 'Normal',
        run: { font: 'Arial', size: 56, bold: true, color: C.title }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 15840, height: 12240 },  // landscape
        margin: { top: 720, right: 720, bottom: 720, left: 720 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [new TextRun({ text: `${storyboard.project} — ${storyboard.episode}`, bold: true, size: 18, color: C.scene })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: 'Generated by 小志 × OpenClaw | ', size: 16, color: '888888' })]
        })]
      })
    },
    children: [
      // ---- TITLE ----
      new Paragraph({
        children: [new TextRun({ text: storyboard.project, bold: true, size: 56, color: C.title })],
        spacing: { before: 0, after: 120 }
      }),
      new Paragraph({
        children: [new TextRun({ text: storyboard.episode, size: 32, color: C.scene })],
        spacing: { before: 0, after: 240 }
      }),

      // ---- META ----
      new Table({
        width: { size: 50, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({ children: [
            new TableCell({ children: [new Paragraph({ children: [bold('Model: ', 18), run(storyboard.model, 18)] })] }),
            new TableCell({ children: [new Paragraph({ children: [bold('Resolution: ', 18), run(storyboard.resolution, 18)] })] }),
            new TableCell({ children: [new Paragraph({ children: [bold('FPS: ', 18), run(`${storyboard.fps}`, 18)] })] }),
            new TableCell({ children: [new Paragraph({ children: [bold('Duration: ', 18), run(`${storyboard.total_duration}s`, 18)] })] }),
          ]})
        ],
      }),
      spacer(),

      // ---- CHARACTERS ----
      new Paragraph({
        children: [new TextRun({ text: 'Character Tracking', bold: true, size: 28, color: C.title })],
        spacing: { before: 360, after: 120 }
      }),
      makeCharacterTable(storyboard.character_tracking),
      spacer(),

      // ---- SCENES ----
      new Paragraph({
        children: [new TextRun({ text: 'Scene Overview', bold: true, size: 28, color: C.title })],
        spacing: { before: 360, after: 120 }
      }),
      makeSceneTable(storyboard.scenes),
      spacer(),

      pageBreak(),

      // ---- SHOTS ----
      new Paragraph({
        children: [new TextRun({ text: 'Shot Breakdown', bold: true, size: 28, color: C.title })],
        spacing: { before: 0, after: 120 }
      }),
      new Paragraph({
        children: [new TextRun({ text: `${storyboard.shots.length} shots total`, size: 18, color: '666666' })],
        spacing: { before: 0, after: 200 }
      }),
      makeShotTable(storyboard.shots),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('storyboard_v2.docx', buf);
  console.log('Done: storyboard_v2.docx');
});
