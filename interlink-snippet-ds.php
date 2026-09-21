<?php
/**
 * Interlink automation v1 — DS (decorativearchitecturalshapes.com)
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
        $rules = json_decode('[{"id":"DS-001","site":"DS","path":"/decorative-architectural-shapes-architectural-columns-capitals-bases/","mode":"replace","phrase":"architectural columns","url":"https://decorativearchitecturalshapes.com/services/architectural-columns/"},{"id":"DS-002","site":"DS","path":"/decorative-architectural-shapes-architectural-columns-capitals-bases/","mode":"append","phrase":"custom column kits","url":"https://decorativearchitecturalshapes.com/services/architectural-columns/"},{"id":"DS-003","site":"DS","path":"/decorative-architectural-shapes-architectural-columns-capitals-bases/","mode":"append","phrase":"column capitals","url":"https://decorativearchitecturalshapes.com/services/column-capitals/"},{"id":"DS-004","site":"DS","path":"/easy-installation-why-pre-assembled-solutions-s/","mode":"replace","phrase":"arches and keystones","url":"https://decorativearchitecturalshapes.com/services/decorative-architectural-arches/"},{"id":"DS-005","site":"DS","path":"/easy-installation-why-pre-assembled-solutions-s/","mode":"append","phrase":"custom architectural arches","url":"https://decorativearchitecturalshapes.com/services/decorative-architectural-arches/"},{"id":"DS-006","site":"DS","path":"/juliet-balcony-functional-kits/","mode":"replace","phrase":"juliet balcony kits","url":"https://decorativearchitecturalshapes.com/services/decorative-juliet-balconies/"},{"id":"DS-007","site":"DS","path":"/juliet-balcony-functional-kits/","mode":"append","phrase":"functional juliet balconies","url":"https://decorativearchitecturalshapes.com/services/decorative-juliet-balconies/"},{"id":"DS-008","site":"DS","path":"/decorative-architectural-shapes-decorative-modern-dormer-windows/","mode":"replace","phrase":"dormer windows","url":"https://decorativearchitecturalshapes.com/services/dormer-windows/"},{"id":"DS-009","site":"DS","path":"/decorative-architectural-shapes-decorative-modern-dormer-windows/","mode":"append","phrase":"custom dormer surrounds","url":"https://decorativearchitecturalshapes.com/services/dormer-windows/"},{"id":"DS-010","site":"DS","path":"/decorative-architectural-shapes-exterior-corbels-and-brackets/","mode":"replace","phrase":"exterior corbels and brackets","url":"https://decorativearchitecturalshapes.com/services/exterior-corbels-brackets/"},{"id":"DS-011","site":"DS","path":"/decorative-architectural-shapes-exterior-corbels-and-brackets/","mode":"append","phrase":"decorative corbels","url":"https://decorativearchitecturalshapes.com/services/exterior-corbels-brackets/"},{"id":"DS-012","site":"DS","path":"/how-to-choose-exterior-polyurethane-trim-for-your-home/","mode":"append","phrase":"exterior decorative trim","url":"https://decorativearchitecturalshapes.com/services/exterior-decorative-trims/"},{"id":"DS-013","site":"DS","path":"/interior-foam-crown-molding-and-decorative-trim-styles-design-ideas-installation-and-benefits/","mode":"replace","phrase":"crown moldings","url":"https://decorativearchitecturalshapes.com/services/crown-moldings/"},{"id":"DS-014","site":"DS","path":"/interior-foam-crown-molding-and-decorative-trim-styles-design-ideas-installation-and-benefits/","mode":"append","phrase":"foam crown molding","url":"https://decorativearchitecturalshapes.com/services/crown-moldings/"},{"id":"DS-015","site":"DS","path":"/interior-foam-crown-molding-and-decorative-trim-styles-design-ideas-installation-and-benefits/","mode":"append","phrase":"decorative moldings","url":"https://decorativearchitecturalshapes.com/services/decorative-moldings/"},{"id":"DS-016","site":"DS","path":"/how-to-install-foam-molding-step-by-step-guide-tools-adhesives-and-common-mistakes/","mode":"replace","phrase":"decorative moldings","url":"https://decorativearchitecturalshapes.com/services/decorative-moldings/"},{"id":"DS-017","site":"DS","path":"/how-to-install-foam-molding-step-by-step-guide-tools-adhesives-and-common-mistakes/","mode":"append","phrase":"foam molding","url":"https://decorativearchitecturalshapes.com/services/decorative-moldings/"},{"id":"DS-018","site":"DS","path":"/exterior-window-shutters-styles-materials-custom-options-and-installation-guide/","mode":"replace","phrase":"exterior louvers","url":"https://decorativearchitecturalshapes.com/services/exterior-louvers/"},{"id":"DS-019","site":"DS","path":"/exterior-window-shutters-styles-materials-custom-options-and-installation-guide/","mode":"append","phrase":"louver and shutter systems","url":"https://decorativearchitecturalshapes.com/services/exterior-louvers/"},{"id":"DS-020","site":"DS","path":"/case-collection/private-residence-privacy-wall-sarasota-fl/","mode":"replace","phrase":"architectural privacy walls","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-022","site":"DS","path":"/case-collection/6-foot-high-decorative-stucco-wall-fence-for-a-corner-lot-home/","mode":"replace","phrase":"decorative stucco wall fence","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-024","site":"DS","path":"/case-collection/private-residence-privacy-wall-ponte-vedra-beach-fl/","mode":"replace","phrase":"residential privacy walls","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-026","site":"DS","path":"/case-collection/luxury-residence-privacy-wall-naples-fl/","mode":"replace","phrase":"luxury privacy walls","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-028","site":"DS","path":"/case-collection/architectural-stucco-privacy-wall-for-a-new-construction-home-tampa-fl/","mode":"replace","phrase":"privacy walls for new construction","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-030","site":"DS","path":"/case-collection/private-residence-stucco-fence-fort-myers-fl/","mode":"replace","phrase":"residential stucco fences","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-032","site":"DS","path":"/case-collection/the-concrete-illusion/","mode":"replace","phrase":"prefab stucco wall systems","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-034","site":"DS","path":"/case-collection/beyond-the-block/","mode":"replace","phrase":"architectural fencing systems","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-036","site":"DS","path":"/case-collection/private-residence-stucco-fence/","mode":"replace","phrase":"decorative stucco fences","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-038","site":"DS","path":"/case-collection/hoa-residential-development-privacy-wall-jacksonville-fl/","mode":"replace","phrase":"HOA privacy walls","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-040","site":"DS","path":"/case-collection/hoa-gated-community-orlando-fl/","mode":"replace","phrase":"community privacy walls","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"},{"id":"DS-042","site":"DS","path":"/case-collection/6-foot-high-decorative-stucco-wall-fence-for-an-estate-residence/","mode":"replace","phrase":"estate privacy fences","url":"https://decorativearchitecturalshapes.com/services/custom-stucco-wall-fence-systems/"}]', true);
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
