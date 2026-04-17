<?php
/**
 * AquaPiscine Configurator - WordPress Shortcode
 * 
 * Usage: [configurator_piscine]
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Register shortcode
 */
function aquapiscine_configurator_shortcode() {
    ob_start();
    ?>
    
    <div id="ap-configurator">
        <!-- Header -->
        <div class="ap-header">
            <div>
                <h2 class="ap-header-title">🏊 Configurator Piscine Inteligent</h2>
                <p class="ap-header-subtitle">Powered by AI - Asistent personalizat</p>
            </div>
        </div>
        
        <!-- Chat messages -->
        <div id="ap-chat-messages"></div>
        
        <!-- Price display -->
        <div id="ap-price-display"></div>
        
        <!-- Input area -->
        <div class="ap-input-area">
            <button id="ap-upload-btn" class="ap-input-btn" title="Încarcă imagine teren">
                📸
            </button>
            <input type="file" id="ap-image-input" accept="image/jpeg,image/jpg,image/png,image/webp">
            <textarea 
                id="ap-user-input" 
                placeholder="Scrie mesajul tău aici..." 
                rows="1"
            ></textarea>
            <button id="ap-send-btn" class="ap-input-btn" title="Trimite mesaj">
                ➤
            </button>
        </div>
    </div>
    
    <?php
    return ob_get_clean();
}
add_shortcode('configurator_piscine', 'aquapiscine_configurator_shortcode');

/**
 * Enqueue scripts and styles
 */
function aquapiscine_configurator_enqueue_scripts() {
    // Only load on pages with shortcode
    global $post;
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'configurator_piscine')) {
        
        // CSS
        wp_enqueue_style(
            'aquapiscine-configurator-css',
            get_template_directory_uri() . '/configurator/configurator.css',
            array(),
            '1.0.0'
        );
        
        // JavaScript
        wp_enqueue_script(
            'aquapiscine-configurator-js',
            get_template_directory_uri() . '/configurator/configurator.js',
            array(),
            '1.0.0',
            true
        );
    }
}
add_action('wp_enqueue_scripts', 'aquapiscine_configurator_enqueue_scripts');

/**
 * Add to functions.php of your theme
 * 
 * Copy this entire file to:
 * wp-content/themes/[your-theme]/configurator/configurator.php
 * 
 * Then add to functions.php:
 * require_once get_template_directory() . '/configurator/configurator.php';
 */
