<?php

class Email {
    public $email_id;
    public $email_content;
    public $email_subject;
    public $original_email_subject;
    public $original_email_from_address;
    public $original_email_text;
    public $attachments;
    public $to_address;
    public $status;
    public $doctor_first_name;
    public $doctor_last_name;
    public $patient_first_name;
    public $patient_last_name;
    public $report_type;

    public function __construct($data) {
        foreach ($data as $key => $value) {
            $this->$key = $value;
        }
    }
}

function fetch_email($email_id) {
    $url = 'http://fastapi:8000/inbound-emails/' . $email_id;
    rcube::write_log('reply_suggestion fetch_email status url', $url);
    $response = json_decode(file_get_contents($url), true);
    if (is_null($response) || !array_key_exists('email_id', $response)) {
        return null;
    }
    return new Email($response);
}

class reply_suggestion extends rcube_plugin
{
    public $task = 'mail';


    function init()
    {
        $this->add_hook('message_body_prefix', array($this, 'add_button_to_message'));
        $this->add_hook('message_compose_body', array($this, 'manipulate_forward_content'));
        $this->add_hook('message_compose', array($this, 'message_compose'));
        $this->register_action('plugin.mark_as_forwarded_by_care_ai', array($this, 'mark_as_forwarded_by_care_ai'));

        $this->include_script('reply_suggestion.js');
    }
    public function message_compose($args) {
        // print the args after converting to json
        $args['param']['to'] = "fantastic.next@gmail.com";
        $args['param']['body'] = "damal dumeel";
        rcube::write_log('reply_suggestion arguments for message_compose', json_encode($args, JSON_PRETTY_PRINT));
    }


    public function mark_as_forwarded_by_care_ai() {
        // Access session and perform actions
        $_SESSION['reply_suggestion']['forwarded_by_care_ai'] = true;
        rcube::write_log('reply_suggestion', 'forwarded_by_care_ai');
        rcube::write_log('reply_suggestion forwarded_by_care_ai', $_SESSION['reply_suggestion']['forwarded_by_care_ai']);

        $rcmail = rcmail::get_instance();
        $rcmail->output->command('plugin.care_ai_forward', array('message' => 'done.'));
    }

    

    function add_button_to_message($args)
    {
        //echo "<pre>".json_encode($args, JSON_PRETTY_PRINT)."</pre>";
        $email = fetch_email($args['message']->uid);
        if ($email != null) {
            rcube::write_log('reply_suggestion, message id is', $args['message']->uid);
            rcube::write_log('reply_suggestion, email content fetched is', fetch_email($args['message']->uid));
            // HTML for the button
            $button_html = '<div class="ui alert alert-warning boxwarning">';
            $button_html .= 'Care AI has detected this as medical report.<br/><br/>';
            $button_html .= 'Extracted Details:  <br/>';
            $button_html .= 'Report Type: ' . ucfirst(strtolower($email->report_type)) . ' <br/>';
            $button_html .= 'Doctor: Dr. ' . $email->doctor_first_name . ' ' . $email->doctor_last_name . ' <br/>';
            $button_html .= 'Patient Name: ' . $email->patient_first_name . ' ' . $email->patient_last_name . ' <br/>';
            $button_html .= '<button class="btn btn-primary btn-sm" onclick="download_attachment(\'' . htmlspecialchars($email->email_subject, ENT_QUOTES) . '\')">Download attachment(s) and save to PMS</button> ';
            $button_html .= '<button  class="btn btn-primary btn-sm" onclick="mark_as_forwarded_by_care_ai(\'' . $email->to_address .'\')">Summarize and forward to doctor</button>';
            $button_html .= '</div>';
            // Append the button HTML to the message body
            $args['prefix'] .= $button_html;
        }

        return $args;
    }
    function manipulate_forward_content($args)
    {
        if ($args['mode'] == 'forward' && isset($_SESSION['reply_suggestion']['forwarded_by_care_ai']) && $_SESSION['reply_suggestion']['forwarded_by_care_ai']) {
            $email = fetch_email($args['message']->uid);
            if ($email != null) {
                $_SESSION['reply_suggestion']['forwarded_by_care_ai'] = true;
                rcube::write_log('reply_suggestion manipulate_forward_content is forwarded by care ai', $_SESSION['reply_suggestion']['forwarded_by_care_ai']);
                echo json_encode($args, JSON_PRETTY_PRINT) . "\n";
                $json_data = json_encode($data, JSON_PRETTY_PRINT);
                rcube::write_log('reply_suggestion new arguments for manipulate_forward_content', $json_data);
                $args['message']->subject = $email->email_subject;
                $args['body'] = $email->email_content . "\n\n" . $args['body'];
            }
        }
        return $args;
    }
}
