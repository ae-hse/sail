// Edit Object
$("div.edit-object").click(function(e) {
    var obj_pk = $(this).attr("id");
    var obj_div = $(this);
    $.post("getintent", {pk: obj_pk},
        function(data) {
            $(obj_div).children("div").children("input:checkbox").each(function(index) {
                if (data.indexOf(parseInt($(this).attr("value"))) != -1) {
                    $(this).prop("checked", true)
                }
            });
        }
    )
    $(this).children("div.edit-attributes").slideToggle();
});