// Edit Object
$("div.edit-attributes a#show-more-attributes").click(function(event) {
	event.preventDefault();
	
	var obj_div = $(this).parent("div.edit-attributes");
	
	obj_div.children("div.attribute-checkbox").slideDown();
	
	obj_div.children("a#show-more-attributes").hide();
});
	
$("div.edit-object a#show-attributes").click(function(event) {
	event.preventDefault();
	
	var obj_div = $(this).parent("div.edit-object");
	var obj_pk = obj_div.attr("id");
	$.post("getintent", {pk: obj_pk},
		function(data) {
			$(obj_div).children("div").children("div.attribute-checkbox").each(function(index) { //children("input:checkbox").each(function(index) {
				if (data.indexOf(parseInt($(this).children("input:checkbox").attr("value"))) != -1) {
					$(this).children("input:checkbox").prop("checked", true)
				}
				else {
					$(this).hide();
				}
			});
		}
	);
    
	obj_div.children("div.edit-attributes").children("a#show-more-attributes").show();
	obj_div.children("div.edit-attributes").slideToggle("fast");
	
	var submit_btn = $(obj_div).children("div").children("input:submit");
	// Submit new intent while user is waiting for response
	$(submit_btn).click(function(event) {
		event.preventDefault();

		$.blockUI({ css: { 
			border: 'none', 
			padding: '15px', 
			backgroundColor: '#000', 
			'-webkit-border-radius': '10px', 
			'-moz-border-radius': '10px', 
			opacity: .5, 
			color: '#fff' 
		} });
		
		var intent = new Array();

		$(obj_div).children("div").children("div.attribute-checkbox").each(function(index) {// children("input:checkbox").each(function(index) {
			if ($(this).children("input:checkbox").prop("checked")) {
				intent.push($(this).children("input:checkbox").attr("value"));
			}
		});

		$.post("submitintent", {pk: obj_pk, 'intent[]': intent},
			function(data) {
				setTimeout($.unblockUI, 1000);
				if (data['status'] != 'ok') {
					alert(data['status']);
					document.location.href = document.location.href;
				}
			}
		);
	});
});

$("a.confirm-imp").click(function(event) {
	event.preventDefault();
	imp_pk = $(this).attr("id")

	$.blockUI({ css: { 
			border: 'none', 
			padding: '15px', 
			backgroundColor: '#000', 
			'-webkit-border-radius': '10px', 
			'-moz-border-radius': '10px', 
			opacity: .5, 
			color: '#fff' 
		} });

	$.post("confirmimplication", {pk: imp_pk},
			function(data) {
				$.unblockUI();
				document.location.href = document.location.href;
			}
	);
});
	
// Confirm objects' deletion
function confirm_object_delete() {
	var answer = confirm("Delete Object?")
	if (answer) {
		document.deleteForm.submit()
	}
}

// Confirm attributes' deletion
function confirm_attribute_delete() {
    var answer = confirm("Delete Attribute?")
    if (answer) {
        document.deleteForm.submit()
    }
}

$("a.unconfirm-imp").click(function(event) {
	event.preventDefault();
	imp_pk = $(this).attr("id")

	$.blockUI({ css: { 
			border: 'none', 
			padding: '15px', 
			backgroundColor: '#000', 
			'-webkit-border-radius': '10px', 
			'-moz-border-radius': '10px', 
			opacity: .5, 
			color: '#fff' 
		} });

	$.post("unconfirmimplication", {pk: imp_pk},
			function(data) {
				$.unblockUI();
				document.location.href = document.location.href;
			}
	);
});

// Rejection
$(document).ready(function() {
	$("a.reject-imp").each(function() {
	  var imp_pk = this.id;
	  $(this).fancybox({
	        'scrolling'		: 'no',
			'titleShow'		: false,
	        'onStart' : function() {
	        	$("#imp_pk").val(imp_pk);
	        	$.post("getpremise", {imp_pk: imp_pk},
	        	function(data) {
                    if (data == "reload") {
                        document.location.href = document.location.href;
                    }
	        		$(".attribute-input").each(function(index) {
				        if (data.indexOf(parseInt($(this).attr("name"))) != -1) {
					       $(this).prop("checked", true)
					       $(this).prop("disabled", true)
				        }
			     });
	        	});
                $.post("getconclusion", {imp_pk: imp_pk},
                function(data) {
                    if (data == "reload") {
                        document.location.href = document.location.href;
                    }
                    
                });
	        }
	  });
	});
});

$("#counterexample_form").bind("submit", function() {

	$.fancybox.showActivity();

	$.post("rejectimplication", $(this).serializeArray(),
			function(data) {
				if (data['status'] != 'ok') {
					alert(data['status']);
			}
			document.location.href = document.location.href;
		}
	);

	return false;
});

$("a.tune_imp").click(function(event) {
    event.preventDefault();
    
    var attr = encodeURIComponent($(this).attr("id"));
    var search_par = parseGetParams();
    var search_new = "";
    for (var i = 0; i < search_par.length; i++) {
        if (search_par[i] != attr) {
            if (search_new != "") {
                search_new = search_new + "&";
            }
            search_new = search_new + "a=" + search_par[i];
        }
    }
    
    if (search_new != "") {
        search_new = "?" + search_new;
    }

    window.location.search = search_new;
    
    function parseGetParams() {
        var res = [];
        var __GET = window.location.search.substring(1).split("&");
        for(var i = 0; i <__GET.length; i++) {
            var getVar = __GET[i].split("=");
            res.push(getVar[1]);            
        }
        return res
    }
});

$(document).ajaxSend(function(event, xhr, settings) {
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
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});