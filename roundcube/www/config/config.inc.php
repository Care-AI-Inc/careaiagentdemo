<?php
    $config['plugins'] = ["reply_suggestion"];
    $config['log_driver'] = 'stdout';
    $config['zipdownload_selection'] = true;
    $config['des_key'] = 'w/rC5gl/rJO/40UgSq0uMT0X';
    $config['enable_spellcheck'] = true;
    $config['imap_cache'] = 'db'; // Enables IMAP cache using the database
    $config['messages_cache'] = 'db'; // Enables message cache using the database
    $config['spellcheck_engine'] = 'pspell';
    $config['imap_cache_ttl'] = '10d'; // Cache IMAP data for 10 days
    $config['imap_timeout'] = 30; // Set IMAP timeout to 30 seconds
    $config['smtp_timeout'] = 30; // Set SMTP timeout to 30 seconds
    $config['prefer_html'] = true; // Prefer HTML over plain text
    $config['list_cols'] = array('subject', 'status', 'fromto', 'date', 'size', 'flag', 'attachment');
    $config['messages_pagesize'] = 50; // Show 50 messages per page
    $config['read_when_deleted'] = false; // Don't mark message as read when deleted
    $config['skip_deleted'] = true; // Skip deleted messages when navigating
    include(__DIR__ . '/config.docker.inc.php');