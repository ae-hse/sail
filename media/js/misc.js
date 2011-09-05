// Edit Object
$("div.edit-object h2").click(function(e) {
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
    $(submit_btn).click(function(e) {

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
                $.unblockUI();
            }
        );
    });
});