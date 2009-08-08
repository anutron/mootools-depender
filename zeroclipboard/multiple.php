<?php
echo '
<html>
<head>
<style type="text/css">
#d_clip_button_1,
#d_clip_button_2,
#d_clip_button_3,
#d_clip_button_4,
#d_clip_button_5,
#d_clip_button_6,
#d_clip_button_7,
#d_clip_button_8,
#d_clip_button_9{
        text-align:center; 
        border:1px solid black; 
        background-color:#ccc; 
        margin:10px; padding:10px; 
}
</style>
</head>
<body>
<script type="text/javascript" src="ZeroClipboard.js"></script>';

for($i=1;$i<=9;$i++) {
        echo '
        <div id="d_clip_button_'.$i.'">'.$i.'00000</div>
        
        <script language="JavaScript">
        var clip = new ZeroClipboard.Client();
        
        clip.setText( \'\' ); // will be set later on mouseDown
        clip.setHandCursor( true );
        clip.addEventListener( \'mouseDown\', function(client) { 
                        // set text to copy here
                        //clip.setText( document.getElementById(\'clip_text\').value );
                        client.setText(\''.$i.'00000\');
        } );
        
        clip.addEventListener( \'complete\', function(client, text) {
        	alert("Copied text to clipboard: " + text );
        } );
                                                
        clip.glue( \'d_clip_button_'.$i.'\' );
        </script>';
}
echo '
</body>
</html>';
?>