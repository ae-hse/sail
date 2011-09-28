// Edit Object
$("div.edit-object a#show-attributes").click(function(event) {
	event.preventDefault();
	
	var obj_div = $(this).parent("div.edit-object");
	var obj_pk = obj_div.attr("id");
	$.post("getintent", {pk: obj_pk},
		function(data) {
			$(obj_div).children("div").children("input:checkbox").each(function(index) {
				if (data.indexOf(parseInt($(this).attr("value"))) != -1) {
					$(this).prop("checked", true)
				}
			});
		}
	);

	obj_div.children("div.edit-attributes").slideToggle();
	
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

		$(obj_div).children("div").children("input:checkbox").each(function(index) {
			if ($(this).prop("checked")) {
				intent.push($(this).attr("value"));
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

$("a.confirm-imp").click(function(e) {
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

$("a.unconfirm-imp").click(function(e) {
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