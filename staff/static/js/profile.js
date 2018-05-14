$(document).ready(function() {
    $('.languages').select2();
    $('.drivercategories').select2();
    $("#id_phone_number").intlTelInput();
    $("#id_emergency_number").intlTelInput();
})
function SubmitSaveprofile(){
    var phonenumb = $("#id_phone_number").intlTelInput("getNumber", intlTelInputUtils.numberFormat.E164);
    var emcnumb = $("#id_emergency_number").intlTelInput("getNumber", intlTelInputUtils.numberFormat.E164);
    document.getElementById('id_phone_number').value = phonenumb;
    document.getElementById('id_emergency_number').value = emcnumb;
    return false;
}