function checkPasswordMatch() {
		var password = $("#id_password").val();
		var confirmPassword = $("#id_password_retyped").val();

		if (password != confirmPassword)
				$("#passwordchecking").html("Passwords do not match!").css({'background-color':'#f8d7da','border-color':'#f5c6cb','color':'#721c24','display':'block'});
		else
				$("#passwordchecking").html("Passwords match.").css({'background-color':'#d4edda','border-color':'#c3e6cb','color':'#155724','display':'block'});

}
