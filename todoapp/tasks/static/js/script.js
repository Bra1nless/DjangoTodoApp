$(document).ready(function () {
    $(document).on('click', '.remove', function () {
        $(this).parent().remove();
    });
    $(document).on('click', '.checkbox', function () {
        $(this).parent().addClass('completed');
        $(this).attr('disabled', true);

        uid = $(this).attr('data-uid');
        $.get("/tasks/complete/"+uid);
        //$.get("/")
    })
})
