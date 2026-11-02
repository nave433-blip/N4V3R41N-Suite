<?php
define('CACHE_DIR', __DIR__ . '/../public/cache');

function deleteDir($dir) {
    if (!is_dir($dir)) return;
    $files = array_diff(scandir($dir), ['.', '..']);
    foreach ($files as $file) {
        (is_dir("$dir/$file")) ? deleteDir("$dir/$file") : unlink("$dir/$file");
    }
    rmdir($dir);
}

foreach (['stage1', 'stage2', 'stage3'] as $stage) {
    $stageDir = CACHE_DIR . '/' . $stage;
    if (!is_dir($stageDir)) continue;
    foreach (scandir($stageDir) as $folder) {
        if ($folder == '.' || $folder == '..') continue;
        $path = "$stageDir/$folder";
        if (is_dir($path) && (time() - filemtime($path) > 600)) deleteDir($path);
    }
}
