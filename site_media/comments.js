// handles csrf for ajax posts

$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});


function prepareDocument(){
	$("#submit_comment").click(addComment);
	$("#comment_form").addClass('hidden');
	$("#add_comment").click(slideToggleCommentForm);
	$("#add_comment").addClass('visible');
	$("#cancel_comment").click(slideToggleCommentForm);
}

// toggle visibility of comment form
function slideToggleCommentForm() {
	$("#comment_form").slideToggle();
	$("#add_comment").slideToggle();
}

/*
function clearFormElements(ele) {
	$(ele).find(':input').each(function() {
		switch(this.type) {
			case 'password':
			case 'select-multiple':
			case 'select-one':
			case 'text':
			case 'textarea':
				$(this).val('');
				break;
			case 'checkbox':
			case 'radio':
				this.checked = false;
		}
	});
}
*/

function resetForm($form) {
	$form.find('input:text, input:password, input:file, select, textarea').val('');
	$form.find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected');
}


function addComment() {
	// create comment object
	var comment = {
		title: $("#id_title").val(),
		content: $("#id_content").val(),
		noteid: $("#id_note").val()
	};
	
	// make request, process response
	$.post("/comment/note/add/", comment,
		function(response) {
			$("#comment_errors").empty();
			// evaluate the "success" parameter
			if (response.success == "True") {
				// disable the submit button to prevent duplicates
				//$("#submit_comment").attr('disabled', 'disabled');
				// if this is the first comment, remove the 'no comments' place holder
				$("#no_comments").empty();
				// add new comment to comments section
				$("#comments").prepend(response.html).slideDown();
				//$("#comment_form").clearFormElements(this.form); ##### Original Clear Form, kept coming up with (xxxxx is not a function)
				resetForm($('#comment_form'));
				// hide form to deter double clicks
				$(slideToggleCommentForm);
				
			}
			else {
				// add error text to the errors div
				$("#comments_errors").append(response.html);
			}
		}, "json");
}



jQuery(document).ready(prepareDocument);