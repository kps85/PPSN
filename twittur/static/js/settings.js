// JavaScript Document

var glob = {
	picHeightL: $("#profilbild-l").height(),
	picHeightM: $("#profilbild-m").height(),
	picHeightS: $("#profilbild-s").height()
	
};

var initialSetup = function() {
	"use strict";
	var marginM = glob.picHeightL - glob.picHeightM;
	var marginS = glob.picHeightL - glob.picHeightS;
	$("#profilbild-m").css({"margin-top": marginM});
	$("#profilbild-s").css({"margin-top": marginS});
	
	$("#profBildUpdate label").html('&nbsp;Profilbild entfernen?');
}

$("#profilbild").delegate("a", "load", initialSetup());

$(window).load(function() {
	"use strict";
	initialSetup();
});

$(window).scroll(function() {
	"use strict";
	initialSetup();
});