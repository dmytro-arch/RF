<?php
/**
 * Interlink automation v1 — DP (decorativearchitecturalproducts.com)
 * ------------------------------------------------------------------
 * WHAT: adds contextual content->service links from the interlink scheme
 * (body-intro = linkify first phrase occurrence, body-final-cta = append
 * a CTA paragraph). Render-time only: the database is NOT modified.
 *
 * INSTALL (WPCode, free version is enough):
 * 1. Plugins > Add New > install "WPCode – Code Snippets".
 * 2. Code Snippets > Add Snippet > Add Your Custom Code > PHP Snippet.
 * 3. Paste this whole file, Location: "Run Everywhere", Save (WPCode
 *    validates PHP syntax on save), then Activate.
 * 4. Open WP Admin > "Interlink Report": check rules count, visit mapped
 *    pages as a guest (incognito), read the log tail (FOUND vs NOT-FOUND).
 * 5. Go live: set INTERLINK_DRY_RUN to false below, clear page cache.
 * ROLLBACK: deactivate this snippet — output returns to original instantly.
 *
 * Generated from interlink-scheme.csv — do not hand-edit rules; regenerate.
 */
if (!defined('ABSPATH')) {
    exit;
}

if (!defined('INTERLINK_DRY_RUN')) {
    define('INTERLINK_DRY_RUN', true); // true = log only, no output changes
}
if (!defined('INTERLINK_LOG')) {
    define('INTERLINK_LOG', WP_CONTENT_DIR . '/uploads/interlink-dryrun.log');
}

function interlink_rules()
{
    static $rules = null;
    if ($rules === null) {
        $rules = json_decode('[{"id":"DP-001","site":"DP","path":"/faux-wood-trusses-the-complete-expert-guide-to-polyurethane-architectural-trusses/","mode":"replace","phrase":"faux wood trusses","url":"https://decorativearchitecturalproducts.com/services/faux-wood-trusses/"},{"id":"DP-002","site":"DP","path":"/faux-wood-trusses-the-complete-expert-guide-to-polyurethane-architectural-trusses/","mode":"append","phrase":"custom polyurethane trusses","url":"https://decorativearchitecturalproducts.com/services/faux-wood-trusses/"},{"id":"DP-003","site":"DP","path":"/front-door-surround-kits-the-complete-expert-guide-to-eps-hard-coat-architectural-entry-surround-systems/","mode":"replace","phrase":"front door surround kits","url":"https://decorativearchitecturalproducts.com/services/front-door-surrounds-kits/"},{"id":"DP-004","site":"DP","path":"/front-door-surround-kits-the-complete-expert-guide-to-eps-hard-coat-architectural-entry-surround-systems/","mode":"append","phrase":"custom entry surround systems","url":"https://decorativearchitecturalproducts.com/services/front-door-surrounds-kits/"},{"id":"DP-005","site":"DP","path":"/faux-wood-beams-made-of-polyurethane-2/","mode":"replace","phrase":"faux wood beams","url":"https://decorativearchitecturalproducts.com/services/custom-faux-wood-beams/"},{"id":"DP-006","site":"DP","path":"/faux-wood-beams-made-of-polyurethane-2/","mode":"append","phrase":"polyurethane beams","url":"https://decorativearchitecturalproducts.com/services/custom-faux-wood-beams/"},{"id":"DP-007","site":"DP","path":"/architectural-column-kits-the-complete-expert-guide-to-eps-hard-coat-column-systems-shafts-capitals-and-bases/","mode":"replace","phrase":"architectural column kits","url":"https://decorativearchitecturalproducts.com/services/architectural-columns-kits/"},{"id":"DP-008","site":"DP","path":"/architectural-column-kits-the-complete-expert-guide-to-eps-hard-coat-column-systems-shafts-capitals-and-bases/","mode":"append","phrase":"EPS column systems","url":"https://decorativearchitecturalproducts.com/services/architectural-columns-kits/"},{"id":"DP-009","site":"DP","path":"/architectural-column-kits-the-complete-expert-guide-to-eps-hard-coat-column-systems-shafts-capitals-and-bases/","mode":"append","phrase":"custom column capitals and bases","url":"https://decorativearchitecturalproducts.com/services/custom-column-capitals-and-bases/"},{"id":"DP-010","site":"DP","path":"/exterior-polyurethane-trim-and-molding-for-homes-benefits-waterproof-properties-durability-and-painting-guide/","mode":"append","phrase":"decorative architectural products","url":"https://decorativearchitecturalproducts.com/services/"},{"id":"DP-011","site":"DP","path":"/ceiling-faux-wood-planks-the-smart-alternative-to-real-timber-for-any-interior/","mode":"replace","phrase":"ceiling faux wood planks","url":"https://decorativearchitecturalproducts.com/services/ceiling-faux-wood-planks/"},{"id":"DP-012","site":"DP","path":"/ceiling-faux-wood-planks-the-smart-alternative-to-real-timber-for-any-interior/","mode":"append","phrase":"faux wood planks for ceilings","url":"https://decorativearchitecturalproducts.com/services/ceiling-faux-wood-planks/"},{"id":"DP-013","site":"DP","path":"/ceiling-dome-design-systems-the-expert-guide-to-eps-hard-coat-architectural-domes-and-ceiling-medallions/","mode":"replace","phrase":"ceiling dome design systems","url":"https://decorativearchitecturalproducts.com/services/ceiling-dome-design-systems/"},{"id":"DP-014","site":"DP","path":"/ceiling-dome-design-systems-the-expert-guide-to-eps-hard-coat-architectural-domes-and-ceiling-medallions/","mode":"append","phrase":"architectural domes and medallions","url":"https://decorativearchitecturalproducts.com/services/ceiling-dome-design-systems/"},{"id":"DP-015","site":"DP","path":"/carved-foam-ceilings-the-complete-expert-guide-to-eps-hard-coat-custom-carved-ceiling-systems/","mode":"replace","phrase":"carved foam ceilings","url":"https://decorativearchitecturalproducts.com/services/carved-foam-ceilings/"},{"id":"DP-016","site":"DP","path":"/carved-foam-ceilings-the-complete-expert-guide-to-eps-hard-coat-custom-carved-ceiling-systems/","mode":"append","phrase":"custom carved ceiling systems","url":"https://decorativearchitecturalproducts.com/services/carved-foam-ceilings/"},{"id":"DP-017","site":"DP","path":"/coffered-ceilings-the-complete-expert-guide-to-eps-hard-coat-custom-ceiling-systems/","mode":"replace","phrase":"coffered ceilings","url":"https://decorativearchitecturalproducts.com/services/custom-coffered-ceilings/"},{"id":"DP-018","site":"DP","path":"/coffered-ceilings-the-complete-expert-guide-to-eps-hard-coat-custom-ceiling-systems/","mode":"append","phrase":"custom coffered ceiling systems","url":"https://decorativearchitecturalproducts.com/services/custom-coffered-ceilings/"},{"id":"DP-019","site":"DP","path":"/custom-column-capitals-bases-the-complete-expert-guide-to-architectural-eps-hard-coat-systems/","mode":"replace","phrase":"custom column capitals and bases","url":"https://decorativearchitecturalproducts.com/services/custom-column-capitals-and-bases/"},{"id":"DP-020","site":"DP","path":"/custom-column-capitals-bases-the-complete-expert-guide-to-architectural-eps-hard-coat-systems/","mode":"append","phrase":"capitals and bases for columns","url":"https://decorativearchitecturalproducts.com/services/custom-column-capitals-and-bases/"},{"id":"DP-021","site":"DP","path":"/case-collection/chatelaine-fence-project/","mode":"replace","phrase":"stucco architectural fencing system","url":"https://decorativearchitecturalproducts.com/services/stucco-architectural-fencing-systems/"},{"id":"DP-023","site":"DP","path":"/case-collection/custom-lightweight-fence-panel-system-with-integrated-lighting/","mode":"replace","phrase":"lightweight fence panel system","url":"https://decorativearchitecturalproducts.com/services/stucco-architectural-fencing-systems/"},{"id":"DP-025","site":"DP","path":"/case-collection/custom-3d-monument-sign-with-realistic-pine-trees/","mode":"append","phrase":"custom architectural products","url":"https://decorativearchitecturalproducts.com/services/"},{"id":"DP-026","site":"DP","path":"/case-collection/decorative-custom-shutters-for-commercial-project/","mode":"append","phrase":"custom architectural products","url":"https://decorativearchitecturalproducts.com/services/"},{"id":"DP-027","site":"DP","path":"/case-collection/custom-decorative-wall-panels-for-outdoor-zoning/","mode":"append","phrase":"custom architectural products","url":"https://decorativearchitecturalproducts.com/services/"},{"id":"DP-028","site":"DP","path":"/case-collection/custom-fireplace-surround-luxury-residential-mantel-design/","mode":"replace","phrase":"fireplace surround kits","url":"https://decorativearchitecturalproducts.com/services/fireplace-surround-kits/"},{"id":"DP-030","site":"DP","path":"/case-collection/custom-fireplace-surround-luxury-residential-mantel-design/","mode":"append","phrase":"faux wood mantels","url":"https://decorativearchitecturalproducts.com/services/faux-wood-mantels/"},{"id":"DP-031","site":"DP","path":"/case-collection/custom-faux-brick-mailbox-for-residential-project/","mode":"replace","phrase":"stucco mailboxes","url":"https://decorativearchitecturalproducts.com/services/stucco-mailboxes-and-lamp-posts-kits/"},{"id":"DP-033","site":"DP","path":"/case-collection/custom-columns-and-trellis-for-residential-project/","mode":"replace","phrase":"architectural column kits","url":"https://decorativearchitecturalproducts.com/services/architectural-columns-kits/"},{"id":"DP-035","site":"DP","path":"/case-collection/custom-decorative-corbels-for-residential-project/","mode":"replace","phrase":"carved corbels","url":"https://decorativearchitecturalproducts.com/services/carved-corbels/"},{"id":"DP-037","site":"DP","path":"/case-collection/xxl-corinthian-column-capitals-for-20-architectural-columns/","mode":"replace","phrase":"Corinthian column capitals","url":"https://decorativearchitecturalproducts.com/services/custom-column-capitals-and-bases/"},{"id":"DP-039","site":"DP","path":"/case-collection/xxl-corinthian-column-capitals-for-20-architectural-columns/","mode":"append","phrase":"20-foot architectural columns","url":"https://decorativearchitecturalproducts.com/services/architectural-columns-kits/"}]', true);
    }
    return is_array($rules) ? $rules : array();
}

function interlink_current_path()
{
    $uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '/';
    $path = parse_url($uri, PHP_URL_PATH);
    return '/' . trim(rawurldecode($path ? $path : '/'), '/');
}

function interlink_rules_for_path($path)
{
    $out = array('replace' => array(), 'append' => array());
    foreach (interlink_rules() as $r) {
        $rp = '/' . trim(rawurldecode($r['path']), '/');
        if ($rp === $path && isset($out[$r['mode']])) {
            $out[$r['mode']][] = $r;
        }
    }
    return $out;
}

function interlink_should_run()
{
    if (is_admin()) {
        return false;
    }
    if (defined('REST_REQUEST') && REST_REQUEST) {
        return false;
    }
    if (function_exists('wp_doing_ajax') && wp_doing_ajax()) {
        return false;
    }
    if (function_exists('wp_doing_cron') && wp_doing_cron()) {
        return false;
    }
    if (is_feed() || is_preview() || (function_exists('is_robots') && is_robots())) {
        return false;
    }
    if (!is_singular()) {
        return false;
    }
    return true;
}

function interlink_log($msg)
{
    $f = INTERLINK_LOG;
    if (file_exists($f) && filesize($f) > 2097152) {
        @rename($f, $f . '.old');
    }
    $tag = INTERLINK_DRY_RUN ? 'DRY' : 'LIVE';
    @file_put_contents($f, '[' . gmdate('Y-m-d H:i:s') . "][$tag] " . $msg . "\n", FILE_APPEND | LOCK_EX);
}

/**
 * Linkify the FIRST occurrence of $phrase in an HTML fragment.
 * DOM-based: never touches text inside <a>/<script>/<style>/<textarea>.
 * Returns array($newHtml, $foundBool).
 */
function interlink_linkify_first($html, $phrase, $url)
{
    if ($html === '' || stripos($html, $phrase) === false) {
        return array($html, false);
    }
    if (!class_exists('DOMDocument')) {
        return array($html, false);
    }
    $prev = libxml_use_internal_errors(true);
    $dom = new DOMDocument('1.0', 'UTF-8');
    $ok = $dom->loadHTML(
        '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>' .
        '<body><div id="ilw">' . $html . '</div></body></html>'
    );
    if (!$ok) {
        libxml_clear_errors();
        libxml_use_internal_errors($prev);
        return array($html, false);
    }
    $xpath = new DOMXPath($dom);
    $nodes = $xpath->query('//div[@id="ilw"]//text()[not(ancestor::a) and not(ancestor::script) and not(ancestor::style) and not(ancestor::textarea)]');
    $pattern = '/\b(' . preg_quote($phrase, '/') . ')\b/iu';
    $done = false;
    if ($nodes) {
        foreach ($nodes as $node) {
            $val = $node->nodeValue;
            if (!preg_match($pattern, $val, $m, PREG_OFFSET_CAPTURE)) {
                continue;
            }
            // PREG_OFFSET_CAPTURE offset is in bytes -> convert to chars.
            $bytePos = $m[0][1];
            $charPos = function_exists('mb_strlen')
                ? mb_strlen(substr($val, 0, $bytePos), 'UTF-8')
                : strlen(substr($val, 0, $bytePos));
            $matched = $m[0][0];
            $charLen = function_exists('mb_strlen') ? mb_strlen($matched, 'UTF-8') : strlen($matched);
            $before = function_exists('mb_substr') ? mb_substr($val, 0, $charPos, 'UTF-8') : substr($val, 0, $charPos);
            $after = function_exists('mb_substr') ? mb_substr($val, $charPos + $charLen, null, 'UTF-8') : substr($val, $charPos + $charLen);
            $doc = $node->ownerDocument;
            $parent = $node->parentNode;
            $a = $doc->createElement('a');
            $a->setAttribute('href', $url);
            $a->textContent = $matched;
            if ($before !== '') {
                $parent->insertBefore($doc->createTextNode($before), $node);
            }
            $parent->insertBefore($a, $node);
            $parent->insertBefore($doc->createComment('il'), $node);
            if ($after !== '') {
                $parent->insertBefore($doc->createTextNode($after), $node);
            }
            $parent->removeChild($node);
            $done = true;
            break; // first occurrence only, page-wide per rule (see caller guard)
        }
    }
    $out = '';
    $wrap = $dom->getElementById('ilw');
    if ($wrap) {
        foreach ($wrap->childNodes as $ch) {
            $out .= $dom->saveHTML($ch);
        }
    }
    libxml_clear_errors();
    libxml_use_internal_errors($prev);
    return array($out === '' ? $html : $out, $done);
}

function interlink_cta_paragraph($rule)
{
    $url = esc_url($rule['url']);
    $anchor = esc_html($rule['phrase']);
    return '<p class="interlink-cta">Ready to specify it for your project? Explore our <a href="' .
        $url . '">' . $anchor . '</a> &mdash; finishes, specs, and a fast project quote.</p><!--il-append-->';
}

/** Recursively collect references to text-element settings arrays. */
function interlink_collect_texts(&$node, &$out)
{
    if (!is_array($node)) {
        return;
    }
    if (isset($node['name'], $node['settings']) && is_array($node['settings'])
        && isset($node['settings']['text']) && is_string($node['settings']['text'])
        && in_array($node['name'], array('text', 'rich-text', 'richtext', 'text-basic'), true)
    ) {
        $out[] = &$node['settings'];
        foreach ($node as $k => &$v) {
            if ($k === 'settings') {
                continue;
            }
            if (is_array($v)) {
                interlink_collect_texts($v, $out);
            }
        }
        unset($v);
        return;
    }
    foreach ($node as $k => &$v) {
        if (is_array($v)) {
            interlink_collect_texts($v, $out);
        }
    }
    unset($v);
}

/** Primary path: Bricks builder data before render (precise targeting). */
function interlink_bricks_filter($data, $post = null, $area = null)
{
    static $appended = false;
    static $replaced = array();
    if (!interlink_should_run() || !is_array($data)) {
        return $data;
    }
    $path = interlink_current_path();
    $rules = interlink_rules_for_path($path);
    if (empty($rules['replace']) && empty($rules['append'])) {
        return $data;
    }
    $texts = array();
    interlink_collect_texts($data, $texts);
    if (empty($texts)) {
        return $data;
    }
    $areaLabel = is_string($area) ? $area : (is_object($area) ? get_class($area) : gettype($area));
    foreach ($rules['replace'] as $r) {
        if (in_array($r['id'], $replaced, true)) {
            continue;
        }
        $found = false;
        foreach ($texts as &$t) {
            list($new, $ok) = interlink_linkify_first($t['text'], $r['phrase'], $r['url']);
            if ($ok) {
                $found = true;
                if (!INTERLINK_DRY_RUN) {
                    $t['text'] = $new;
                }
                break;
            }
        }
        unset($t);
        if ($found) {
            $replaced[] = $r['id'];
        }
        interlink_log($r['id'] . ' path:' . $path . ' hook:bricks(' . $areaLabel . ') REPLACE "' .
            $r['phrase'] . '" => ' . ($found ? 'FOUND' : 'NOT-FOUND'));
    }
    if (!$appended && !empty($rules['append'])) {
        $isContent = ($area === null)
            || (is_string($area) && stripos($area, 'content') !== false)
            || count($texts) >= 3;
        if ($isContent) {
            $cta = '';
            $ids = array();
            foreach ($rules['append'] as $r) {
                $cta .= interlink_cta_paragraph($r);
                $ids[] = $r['id'];
            }
            if (!INTERLINK_DRY_RUN) {
                $last = count($texts) - 1;
                $texts[$last]['text'] .= $cta;
            }
            interlink_log(implode(',', $ids) . ' path:' . $path . ' hook:bricks(' . $areaLabel .
                ') APPEND ' . count($rules['append']) . ' cta-paragraph(s)');
            $appended = true;
        }
    }
    $GLOBALS['interlink_bricks_touched'] = true;
    return $data;
}

/** Fallback path: classic the_content (only if Bricks filter never fired). */
function interlink_content_filter($content)
{
    if (!interlink_should_run()) {
        return $content;
    }
    if (!empty($GLOBALS['interlink_bricks_touched'])) {
        return $content;
    }
    if (!in_the_loop() || !is_main_query()) {
        return $content;
    }
    $path = interlink_current_path();
    $rules = interlink_rules_for_path($path);
    if (empty($rules['replace']) && empty($rules['append'])) {
        return $content;
    }
    foreach ($rules['replace'] as $r) {
        list($new, $found) = interlink_linkify_first($content, $r['phrase'], $r['url']);
        if ($found && !INTERLINK_DRY_RUN) {
            $content = $new;
        }
        interlink_log($r['id'] . ' path:' . $path . ' hook:the_content REPLACE "' .
            $r['phrase'] . '" => ' . ($found ? 'FOUND' : 'NOT-FOUND'));
    }
    if (!empty($rules['append'])) {
        $ids = array();
        foreach ($rules['append'] as $r) {
            if (!INTERLINK_DRY_RUN) {
                $content .= interlink_cta_paragraph($r);
            }
            $ids[] = $r['id'];
        }
        interlink_log(implode(',', $ids) . ' path:' . $path . ' hook:the_content APPEND ' .
            count($rules['append']) . ' cta-paragraph(s)');
    }
    return $content;
}

function interlink_report_page()
{
    if (!current_user_can('manage_options')) {
        return;
    }
    echo '<div class="wrap"><h1>Interlink Report</h1>';
    echo '<p>Site file: <code>interlink-snippet v1</code> &nbsp;|&nbsp; Mode: <strong>' .
        (INTERLINK_DRY_RUN ? 'DRY-RUN (logging only, no changes)' : 'LIVE') . '</strong></p>';
    $rules = interlink_rules();
    echo '<h2>Rules loaded: ' . count($rules) . '</h2>';
    echo '<table class="widefat striped"><thead><tr><th>ID</th><th>Source path</th><th>Mode</th><th>Anchor / phrase</th><th>Target</th></tr></thead><tbody>';
    foreach ($rules as $r) {
        echo '<tr><td>' . esc_html($r['id']) . '</td><td><code>' . esc_html($r['path']) .
            '</code></td><td>' . esc_html($r['mode']) . '</td><td>' . esc_html($r['phrase']) .
            '</td><td><code>' . esc_html($r['url']) . '</code></td></tr>';
    }
    echo '</tbody></table>';
    echo '<h2>Log tail (last 200 lines)</h2><pre style="max-height:420px;overflow:auto;background:#fff;border:1px solid #ccd0d4;padding:12px;">';
    if (file_exists(INTERLINK_LOG)) {
        $lines = file(INTERLINK_LOG);
        echo esc_html(implode('', array_slice($lines ? $lines : array(), -200)));
    } else {
        echo 'No log yet. Visit a mapped page on the frontend as a guest (incognito) to generate entries.';
    }
    echo '</pre></div>';
}

add_filter('bricks/frontend/render_data', 'interlink_bricks_filter', 20, 3);
add_filter('the_content', 'interlink_content_filter', 30);
add_action('admin_menu', function () {
    add_menu_page(
        'Interlink Report',
        'Interlink Report',
        'manage_options',
        'interlink-report',
        'interlink_report_page',
        'dashicons-admin-links',
        90
    );
});
