

// Opera 8.0+
var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;

// Firefox 1.0+
var isFirefox = typeof InstallTrigger !== 'undefined';

// Safari 3.0+ "[object HTMLElementConstructor]" 
//var isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && safari.pushNotification));
var isSafari = navigator.vendor && navigator.vendor.indexOf('Apple') > -1 &&
    navigator.userAgent &&
    navigator.userAgent.indexOf('CriOS') == -1 &&
    navigator.userAgent.indexOf('FxiOS') == -1;

// Internet Explorer 6-11
var isIE = /*@cc_on!@*/false || !!document.documentMode;

// Edge 20+
var isEdge = !isIE && !!window.StyleMedia;

// Chrome 1 - 79
var isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);

// Edge (based on chromium) detection
var isEdgeChromium = isChrome && (navigator.userAgent.indexOf("Edg") != -1);

// Blink engine detection
var isBlink = (isChrome || isOpera) && !!window.CSS;

// Get the user-agent string 
let userAgentString =
    navigator.userAgent;

// Detect Chrome 
let chromeAgent =
    userAgentString.indexOf("Chrome") > -1;

// Detect Internet Explorer 
let IExplorerAgent =
    userAgentString.indexOf("MSIE") > -1 ||
    userAgentString.indexOf("rv:") > -1;

// Detect Firefox 
let firefoxAgent =
    userAgentString.indexOf("Firefox") > -1;

// Detect Safari 
let safariAgent =
    userAgentString.indexOf("Safari") > -1;

// Discard Safari since it also matches Chrome 
if ((chromeAgent) && (safariAgent))
    safariAgent = false;

// Detect Opera 
let operaAgent =
    userAgentString.indexOf("OP") > -1;

// Discard Chrome since it also matches Opera      
if ((chromeAgent) && (operaAgent))
    chromeAgent = false; 

/*if (!isSafari && !isChrome  && !chromeAgent) {
    alert("You must use Chrome on Android or PC, or Safari on IOS");
    window.location = "/";
}*/
