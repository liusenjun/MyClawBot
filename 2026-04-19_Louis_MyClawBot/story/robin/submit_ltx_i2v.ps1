$ErrorActionPreference = 'Continue'
$COMFY_URL = 'http://127.0.0.1:8188'

$wf = Get-Content 'C:\Users\user.V915-31\.openclaw\workspace\story\robin\ltx_i2v_workflow.json' | ConvertFrom-Json

$linkMap = @{}
foreach ($link in $wf.links) {
    if ($link) {
        $linkMap[$link[0]] = @($link[1], $link[2])
    }
}

$prompt = @{}
foreach ($n in $wf.nodes) {
    $nid = [string]$n.id
    $inputs = @{}
    
    foreach ($inp in $n.inputs) {
        if ($inp.link -ne $null -and $linkMap.ContainsKey($inp.link)) {
            $srcInfo = $linkMap[$inp.link]
            $inputs[$inp.name] = @([string]$srcInfo[0], $srcInfo[1])
        }
    }
    
    $wv = $n.widgets_values
    switch ($n.type) {
        'VAELoaderKJ' { if ($wv) { $inputs['vae_name'] = $wv[0] } }
        'UnetLoaderGGUF' { if ($wv) { $inputs['model_path'] = $wv[0] } }
        'DualCLIPLoader' { if ($wv -and $wv.Count -ge 2) { $inputs['clip_model1'] = $wv[0]; $inputs['clip_model2'] = $wv[1] } }
        'CLIPTextEncode' { if ($wv) { $inputs['text'] = $wv[0] } }
        'LoraLoaderModelOnly' { if ($wv -and $wv.Count -ge 2) { $inputs['lora_name'] = $wv[0]; $inputs['strength_model'] = $wv[1] } }
        'PrimitiveInt' { if ($wv) { $inputs['value'] = $wv[0] } }
        'PrimitiveFloat' { if ($wv) { $inputs['value'] = $wv[0] } }
        'PrimitiveNode' { 
            $outName = ($n.outputs | Where-Object { $_.widget }).ForEach({ $_.widget.name }) | Select-Object -First 1
            if ($outName -and $wv) { $inputs[$outName] = $wv[0] }
        }
        'LoadImageOutput' { $inputs['image'] = $null }
        'SaveVideo' { if ($wv) { $inputs['filename_prefix'] = $wv[0] } }
        'GetImageRangeFromBatch' { if ($wv -and $wv.Count -ge 2) { $inputs['start_index'] = $wv[0]; $inputs['max_images'] = $wv[1] } }
        'CreateVideo' { if ($wv) { $inputs['fps'] = $wv[0] } }
        'LTXVScheduler' { if ($wv -and $wv.Count -ge 5) { $inputs['steps'] = $wv[0]; $inputs['cfg'] = $wv[1]; $inputs['denoise'] = $wv[2] } }
        'LTXVConditioning' { if ($wv) { $inputs['frame_rate'] = $wv[0] } }
        'LTXVEmptyLatentAudio' { if ($wv -and $wv.Count -ge 3) { $inputs['frames_number'] = $wv[0]; $inputs['frame_rate'] = $wv[1] } }
        'EmptyLTXVLatentVideo' { if ($wv -and $wv.Count -ge 4) { $inputs['width'] = $wv[0]; $inputs['height'] = $wv[1]; $inputs['length'] = $wv[2] } }
        'LTXVSpatioTemporalTiledVAEDecode' { if ($wv -and $wv.Count -ge 6) { $inputs['tile_sample_min_height'] = $wv[0]; $inputs['tile_sample_min_width'] = $wv[1]; $inputs['tile_sample_min_t'] = $wv[2] } }
        'PathchSageAttentionKJ' { if ($wv -and $wv.Count -ge 2) { $inputs['attention_type'] = $wv[0]; $inputs['enable'] = $wv[1] } }
        'LTXVChunkFeedForward' { if ($wv -and $wv.Count -ge 2) { $inputs['chunk_size'] = $wv[0]; $inputs['chunk_nums'] = $wv[1] } }
        'KSamplerSelect' { if ($wv) { $inputs['sampler_name'] = $wv[0] } }
        'CM_FloatToInt' { if ($wv) { $inputs['a'] = $wv[0] } }
        'RandomNoise' { if ($wv) { $inputs['seed'] = $wv[0] } }
        'CFGGuider' { if ($wv) { $inputs['cfg'] = $wv[0] } }
        'LTXVImgToVideoInplace' { if ($wv -and $wv.Count -ge 2) { $inputs['strength'] = $wv[0] } }
    }
    
    $prompt[$nid] = @{ inputs = $inputs; class_type = $n.type }
}

$body = @{ prompt = $prompt } | ConvertTo-Json -Depth 20
$body | Out-File -FilePath $env:TEMP\ltx_prompt.json -Encoding UTF8

try {
    $r = Invoke-WebRequest -Uri "$COMFY_URL/prompt" -Method POST -ContentType 'application/json' -Body ([System.IO.File]::ReadAllText("$env:TEMP\ltx_prompt.json")) -TimeoutSec 30
    Write-Host 'Status:' $r.StatusCode
    $r.Content | ConvertFrom-Json | ConvertTo-Json -Depth 5
} catch {
    Write-Host 'Error:' $_.Exception.Message
    try {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = [System.IO.StreamReader]::new($stream)
        Write-Host 'Body:' $reader.ReadToEnd()
    } catch {}
}
