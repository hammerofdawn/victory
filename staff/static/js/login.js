function checkPasswordMatch() {
	var password = $("#id_password1").val();
	var confirmPassword = $("#id_password2").val();

	if (password != confirmPassword)
		$("#passwordchecking").html("Passwords do not match!").css({'background-color':'#f8d7da','border-color':'#f5c6cb','color':'#721c24','display':'block'});
	else
		$("#passwordchecking").html("Passwords match.").css({'background-color':'#d4edda','border-color':'#c3e6cb','color':'#155724','display':'block'});
}

function checkPasswordMatchVer2() {
	var password = $("#id_new_password1").val();
	var confirmPassword = $("#id_new_password2").val();

	if (password != confirmPassword)
		$("#passwordchecking").html("Passwords do not match!").css({'background-color':'#f8d7da','border-color':'#f5c6cb','color':'#721c24','display':'block'});
	else
		$("#passwordchecking").html("Passwords match.").css({'background-color':'#d4edda','border-color':'#c3e6cb','color':'#155724','display':'block'});
}

$(document).ready(function() {
	$("#id_phone_number").intlTelInput();
	$("#id_password1, #id_password2").keyup(checkPasswordMatch);
})

function SubmitRegister(){
	var phonenumb = $("#id_phone_number").intlTelInput("getNumber", intlTelInputUtils.numberFormat.E164);
	document.getElementById('id_phone_number').value = phonenumb;
	document.getElementsByName('registerform').submit();
}