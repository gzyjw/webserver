	
(function ($) {	
	
    //全局系统对象
    window['LG'] = {};

    //右下角的提示框
    LG.tip = function (message) {
        if (LG.wintip) {
            LG.wintip.set('content', message);
            LG.wintip.show();
        }
        else {
            LG.wintip = $.ligerDialog.tip({ content: message });
        }
        setTimeout(function () {
            LG.wintip.hide()
        }, 4000);
    };

    //预加载图片
    LG.prevLoadImage = function (rootpath, paths) {
        for (var i in paths) {
            $('<img />').attr('src', rootpath + paths[i]);
        }
    };
    //显示loading
    LG.showLoading = function (message) {
        message = message || "正在加载中...";
        $('body').append("<div class='jloading'>" + message + "</div>");
        $.ligerui.win.mask();
    };
    //隐藏loading
    LG.hideLoading = function (message) {
        $('body > div.jloading').remove();
        $.ligerui.win.unmask({ id: new Date().getTime() });
    }

    /*********************************************************************************
    *创建时间：2014/9/16 16:20:36
    *创建人员：刘翔
    *功    能：消息提示
    *********************************************************************************/

    //显示成功提示窗口
    LG.showSuccess = function (message, callback) {
        //window.top.SetHideMsgError();
        if (typeof (message) == "function" || arguments.length == 0) {
            callback = message;
            message = "操作成功!";
        }
        return $.ligerDialog.success(message, '系统信息', callback,{allowClose:false});
    };
    //显示失败提示窗口
    LG.showError = function (message, callback) {
        if (typeof (message) == "function" || arguments.length == 0) {
            callback = message;
            message = "操作失败!";
        }
        return $.ligerDialog.error(message, '系统信息', callback);
    };
    function isArray(obj) {
        return Object.prototype.toString.call(obj) === '[object Array]';
    }
    //显示表单验证错误信息
    LG.showFormError = function (result) {
        if (isArray(result)) {
            $("#MsgDrigg", parent.document).show();
            var html = "";
            for (var i = 0, len = result.length; i < len; i++) {
                html += "<tr><td class='msgrowno'>" + (i + 1) + "</td><td class='msgtitle'>" + result[i].LabelText + "</td><td class='msgcotent'>" + result[i].Message + "</td></tr>"
            }
            $("#MsgTable tbody", parent.document).empty().append(html);
        } else {
            LG.showError(result);
        }
    }
    //前端 显示表单验证错误信息
    LG.showFormErrorTip = function (result) {//result数组："表单类型:MSG0018", "表单:MSG0018"
        if (isArray(result)) {
            $("#MsgDrigg", parent.document).show();
            var html = "";
            for (var i = 0, len = result.length; i < len; i++) {
                html += "<tr><td class='msgrowno'>" + (i + 1) + "</td><td class='msgtitle'>" + result[i].LabelText + "</td><td class='msgcotent'>" + GetMsg(result[i].Message).format(result[i].LabelText) + "</td></tr>"
            }
            $("#MsgTable tbody", parent.document).empty().append(html);
        } else {
            LG.showError(result);
        }
    }

    ///消息提示框调用函数
    ///msgCode：消息编号
    ///msgType：消息类型，参考msgType枚举
    ///param: 替换参数
    LG.showMessage = function (msgCode, msgType,param) { 
        var msg = GetMsg(msgCode,param);

        var msgTypeInfo = "";

        if (msgType == 1) {

            msgTypeInfo = "success";
        }
        else if (msgType == 2) {

            msgTypeInfo = "error";
        }
        else if (msgType == 3) {

            msgTypeInfo = "warn";
        }

        return $.ligerDialog.alert(msg, '系统信息', msgTypeInfo, null, null);
    }

    LG.showMessageExtend = function (extend,msgCode, msgType,param) { 
        var msg = extend + GetMsg(msgCode,param);

        var msgTypeInfo = "";

        if (msgType == 1) {

            msgTypeInfo = "success";
        }
        else if (msgType == 2) {

            msgTypeInfo = "error";
        }
        else if (msgType == 3) {

            msgTypeInfo = "warn";
        }

        return $.ligerDialog.alert(msg, '系统信息', msgTypeInfo, null, null);
    }
    
    /**
     * 提示
     * @param msgCode 
     * @param title
     * @param msgType [success、error、warn、''/none]
     * @param param
     */
    LG.Alert=function(msgCode,title,msgType,param){
    	 var msg = GetMsg(msgCode,param);
    	 var msgTypeInfo = "";
 
    	 $.ligerDialog.alert(msg, title, msgType);    	
    }
    
    LG.AlertMsg=function(msg,title,msgType,param){
   	 var msgTypeInfo = "";

   	 $.ligerDialog.alert(msg, title, msgType);    	
   }
    
    ///自定义确认提示框
    LG.showConfirm = function (msgCode,param, callback) {
    	//alert(param);
    	
        var msg = GetMsg(msgCode,param);

        return $.ligerDialog.confirm(msg, '系统信息', callback);
    }
    
    ///删除数据时，确认删除提示框
    LG.showDeleteConfirm = function (callback) {

        var msg = GetMsg("CP0001","删除");

        return $.ligerDialog.confirm(msg, '系统信息', callback);
    }
    
    // add by wjsh 2018-06-01 begin
    // 自定义删除确认提示框
    LG.showDeleteConfirmCustom = function (msgcode, callback) {
    	
    	var msg = GetMsg(msgcode, "删除");
    	
    	return $.ligerDialog.confirm(msg, '系统信息', callback);
    	
    }
    // add by wjsh 2018-06-01 end

    ///删除数据时，未选择数据提示信息
    LG.showDeleteInfo = function () {

        var msg = GetMsg("WX0001");

        return $.ligerDialog.alert(msg, '系统信息', 'warn', null, null);
    }

    LG.showWarnningInfo = function (msgCode) {

        var msg = GetMsg(msgCode);

        return $.ligerDialog.alert(msg, '系统信息', 'warn', null, null);
    }

    LG.showWaiting = function () {

        var msg = GetMsg("IX0002");
        $.ligerDialog.waitting(msg);
    }

    ///获取消息
    function GetMsg(msgCode,param) {

    	var path ="rest/getMsg";    
        var msg;
        $.ajax({
            cache: false,
            async: false,
            url: path,
            dataType: 'json',
            type: 'post',
            data : [ {
				name : "msgCode",
				value : msgCode
			}],
            success: function (message) {
            	 if(typeof(param)==undefined)
        		 {
        		 	param="";
        		 }  
            	 //alert(message);
        		 msg = message.replace(/\{0}/g,param); 
            }
        });

        return msg;
    }
    
    LG.GetMsg = function (msgCode) { 
    	var path = "rest/getMsg";  
        var msg = "";
        $.ajax({
            cache: false,
            async: false,
            url: path,
            dataType: 'json',
            type: 'post',
            data : [ {
				name : "msgCode",
				value : msgCode
			}],
            success: function (message) {            	
                msg = message;
            }
        });

        return msg;
    }

    //打开窗口
    LG.Open = function (url, width, height, title) {
        return $.ligerDialog.open(
                                    {
                                        url: url,
                                        height: height,
                                        width: width,
                                        title: title
                                    }
                                 );
    }

    LG.OpenWin = function (url, width, height, title) {
        var m = $.ligerDialog.open(
                                    {
                                        url: url,
                                        height: height,
                                        width: width,
                                        title: title
                                    }
                                 );
        m.unmask();
    }

	//打开窗口-显示最大按钮
    LG.OpenShowMax = function (url, width, height, title) {
        return $.ligerDialog.open(
        {
            url: url,
            height: height,
            width: width,
            title: title,
            showMax: true
        }
        );
    }

    /*********************************************************************************
    END
    *********************************************************************************/

    //预加载dialog的图片
    LG.prevDialogImage = function (rootPath) {
        rootPath = rootPath || "";
        LG.prevLoadImage(rootPath + 'Themes/Default/images/win/', ['dialog-icons.gif']);
        LG.prevLoadImage(rootPath + 'Themes/Default/images/win/', ['dialogicon.gif']);
    };

//    //提交服务器请求
//    //返回json格式
//    //1,提交给类 options.type  方法 options.method 处理
//    //2,并返回 AjaxResult(这也是一个类)类型的的序列化好的字符串
//    LG.ajax = function (options) {
//        var p = options || {};
//        var ashxUrl = options.ashxUrl || "/AjaxHandler/ajax.ashx?";
//
//        //var url = p.url || ashxUrl + $.param({ type: p.type, method: p.method });
//         
//        var url = p.url || ashxUrl + "&" + $.param({ system: p.system });
//        $.ajax({
//            cache: false,
//            async: false,
//            url: url,
//            data: p.data,
//            dataType: 'json',
//            type: 'post',
//            beforeSend: function () {
//                LG.loading = true;
//                if (p.beforeSend)
//                    p.beforeSend();
//                else
//                    LG.showLoading(p.loading);
//            },
//            complete: function () {
//                LG.loading = false;
//                if (p.complete)
//                    p.complete();
//                else
//                    LG.hideLoading();
//            },
//            success: function (result) {
//                if (!result) return;
//                if (!result.IsError) {
//                    if (p.success)
//                        p.success(result.Data, result.Message);
//                }
//                else {
//                    if (p.error)
//                        p.error(result.Message);
//                }
//            },
//            error: function (result, b) {
//                alert(result.status);
//                //LG.tip('发现系统错误 <BR>错误码：' + result.status);
//            }
//        });
//    };

    //获取当前页面的MenuNo
    //优先级1：如果页面存在MenuNo的表单元素，那么加载它的值
    //优先级2：加载QueryString，名字为MenuNo的值
    LG.getPageMenuNo = function () {
        var menuno = $("#MenuNo").val();
        if (!menuno) {
            menuno = getQueryStringByName("MenuNo");
        }
        return menuno;
    };

    //创建按钮
    LG.createButton = function (options) {
        var p = $.extend({
            appendTo: $('body')
        }, options || {});
        var btn = $('<div class="button button2 buttonnoicon" style="width:60px"><div class="button-l"> </div><div class="button-r"> </div> <span></span></div>');
        if (p.icon) {
            btn.removeClass("buttonnoicon");
            btn.append('<div class="button-icon"> <img src="../' + p.icon + '" /> </div> ');
        }
        //绿色皮肤
        if (p.green) {
            btn.removeClass("button2");
        }
        if (p.width) {
            btn.width(p.width);
        }
        if (p.click) {
            btn.click(p.click);
        }
        if (p.text) {
            $("span", btn).html(p.text);
        }
        if (typeof (p.appendTo) == "string") p.appendTo = $(p.appendTo);
        btn.appendTo(p.appendTo);
    };

    //创建工具栏  右边标识
    LG.appendToolBarRight = function (str_background, str_color) {
        var str = "";
        if (typeof (str_color) != "undefined" && str_color != "")
            str += "<div style='float:right;height:20px;line-height:20px;font-size:12px;padding-left:5px;'><font color='red'>字体说明:</font>" + str_color + "</div>";
        if (typeof (str_background) != "undefined" && str_background != "")
            str += "<div style='float:right;height:20px;line-height:20px;font-size:12px;'><font color='red'>背景说明:</font>" + str_background + "</div>";
        //$(".l-toolbar-item-right").append(str);
        $(".l-panel-topbar").append(str);
    };

    //快速设置表单底部默认的按钮:保存、取消
    LG.setFormDefaultBtn = function (cancleCallback, savedCallback) {
        //表单底部按钮
        var buttons = [];
        if (cancleCallback) {
            buttons.push({ text: '取消', onclick: cancleCallback });
        }
        if (savedCallback) {
            buttons.push({ text: '保存', onclick: savedCallback });
        }
        LG.addFormButtons(buttons);
    };

    //填充表单数据
    LG.loadForm = function (mainform, options, callback) {
        options = options || {};
        if (!mainform)
            mainform = $("form:first");
        var p = $.extend({
            beforeSend: function () {
                LG.showLoading('正在加载表单数据中...');
            },
            complete: function () {
                LG.hideLoading();
            },
            success: function (data) {
                var preID = options.preID || "";
                //根据返回的属性名，找到相应ID的表单元素，并赋值
                for (var p in data) {
                    var ele = $("[name=" + (preID + p) + "]", mainform);
                    //针对复选框和单选框 处理
                    if (ele.is(":checkbox,:radio")) {
                        ele[0].checked = data[p] ? true : false;
                    }
                    else {
                        ele.val(data[p]);
                    }
                }
                //下面是更新表单的样式
                var managers = $.ligerui.find($.ligerui.controls.Input);
                for (var i = 0, l = managers.length; i < l; i++) {
                    //改变了表单的值，需要调用这个方法来更新ligerui样式
                    var o = managers[i];
                    o.updateStyle();
                    if (managers[i] instanceof $.ligerui.controls.TextBox)
                        o.checkValue();
                }
                if (callback)
                    callback(data);
            },
            error: function (message) {
                LG.showError('数据加载失败!<BR>错误信息：' + message);
            }
        }, options);
        LG.ajax(p);
    };

    //带验证、带loading的提交
    LG.submitForm = function (mainform, success, error, datatype) {
        if (datatype != "text") {
            datatype = "json";
        }
        if (!mainform)
            mainform = $("form:first");

        mainform.ajaxSubmit({
            dataType: datatype,
            success: success,
            beforeSubmit: function (formData, jqForm, options) {
                //针对复选框和单选框 处理
                $(":checkbox,:radio", jqForm).each(function () {
                    if (this.name!="" && !existInFormData(formData, this.name)) {
                        formData.push({ name: this.name, type: this.type, value: this.checked });
                    }
                });
                for (var i = 0, l = formData.length; i < l; i++) {
                    var o = formData[i];                    
                    if ((o.type == "checkbox" || o.type == "radio") && o.name != "") {
                    	o.value = $("[name=" + o.name + "]", jqForm)[0].checked ? "true" : "false";
                    }
                }
            },
            beforeSend: function (a, b, c) {
                LG.showLoading('正在保存数据中...');

            },
            complete: function () {
                LG.hideLoading();
            },
            error: function (result) {
                LG.tip('发现系统错误 <BR>错误码：' + result.status);
            }
        });

        function existInFormData(formData, name) {
            for (var i = 0, l = formData.length; i < l; i++) {
                var o = formData[i];
                if (o.name == name) return true;
            }
            return false;
        }
    };

    LG.loadToolbar = function (grid, toolbarBtnItemClick) {
    	
    	var path ="rest/getfuncmenu";   
    	
        $.ajax({
            cache: false,
            async: false,
            url: path,
            data: [{ name: "pagePath", value: getPageURLPath()}],
            dataType: "json",
            type: "post",
            success: function (result) {   
             	if(typeof(result)=="undefined")
         		{ 
             		//alert(result);
             		if(result.indexOf("<script language=")>-1)
             		{
             			
             			document.write(result);
             		}
         		}else
         		{
	                if ($("#hidQX").val() == undefined) {
	                    $("body").append("<input type='hidden' id='hidQX' name='hidQX' value=''/>");
	                }
	                var qx = ",";
	                if (!grid.toolbarManager) return;
	                if (!result.Data || !result.Data.length) return;
	                var items = [];
	                //用户的按钮权限        
	                for (var i = 0, l = result.Data.length; i < l; i++) {
	                    qx += result.Data[i].functionKey + ",";
	                    if (result.Data[i].isShowFunction == "1") {
	                        var o = result.Data[i];
	                        items[items.length] = {
	                            click: toolbarBtnItemClick,
	                            text: o.navItemText,
	                            img: "",
	                            id: o.functionKey //黄科源 修改为用FunctionKey
	                        };
	                        items[items.length] = { line: true };
	                    }
	                }
	                grid.toolbarManager.set("items", items);
	                if (qx != ",") {
	                    $("#hidQX").val(qx);
	                }
         		}
            },
            error:function(result){
         
            	  var win = parent || window;
            	  if ($("#hidQX").val() == undefined) {
	                    $("body").append("<input type='hidden' id='hidQX' name='hidQX' value=''/>");
	              }
            	  win.LG.RedictLogin(); 
            }
        });
    };
    
    
    
    
    
    
    
    LG.loadDetailsToolbar = function (grid, pagePath,showFunction,toolbarBtnItemClick) {
    	var path ="rest/getfuncmenu";   
    	
        $.ajax({
            cache: false,
            async: false,
            url: path,
            data: [{ name: "pagePath", value: pagePath}],
            dataType: "json",
            type: "post",
            success: function (result) {
            	
             	if(typeof(result)=="undefined")
         		{ 
             		
             		if(result.indexOf("<script language=")>-1)
             		{
             			
             			document.write(result);
             		}
         		}else
         		{         		 
	                if ($("#hidQX").val() == undefined) {
	                    $("body").append("<input type='hidden' id='hidQX' name='hidQX' value=''/>");
	                }
	                var qx = ",";
	                if (!grid.toolbarManager) return;
	                if (!result.Data || !result.Data.length) return;
	                var items = [];
	                //用户的按钮权限        
	                for (var i = 0, l = result.Data.length; i < l; i++) {
	                	
	                	var functionKey=result.Data[i].functionKey;
	                	
	                   var key=functionKey.split("_");
	                   
	                   if(key.length>1 && key[0]=="detail"){
	                	   qx += result.Data[i].functionKey + ",";  
	                	   
	                	   
	                	   if(LG.isShowFunction(functionKey,showFunction)){           		   
	                	  
		                    //if (result.Data[i].isShowFunction == "1") {
		                        var o = result.Data[i];
		                        items[items.length] = {
		                            click: toolbarBtnItemClick,
		                            text: o.navItemText,
		                            img: "",
		                            id: o.functionKey //黄科源 修改为用FunctionKey
		                        };
		                        items[items.length] = { line: true };
		                    //}                	   
	                	   }
	                   }
	                	
	                }
	                grid.toolbarManager.set("items", items);
	                if (qx != ",") {
	                    $("#hidQX").val(qx);
	                }
         		}
            },
            error:function(result){ 
            	  var win = parent || window;
            	  if ($("#hidQX").val() == undefined) {
	                    $("body").append("<input type='hidden' id='hidQX' name='hidQX' value=''/>");
	              }
            	  win.LG.RedictLogin(); 
            }
        });
    };
    

    LG.isShowFunction=function(jurisdictionFunction ,showFunction){
    	
    	if(showFunction!=undefined && showFunction.length>0&&jurisdictionFunction!=undefined){
    		
    		for(var i=0;i<showFunction.length;i++){
    			if(jurisdictionFunction==showFunction[i])
    				return true;
    		}
    		
    	}  
    	
    	return false;
    	
    	
    }
    //覆盖页面grid的loading效果
    LG.overrideGridLoading = function () {
        $.extend($.ligerDefaults.Grid, {
            onloading: function () {
                LG.showLoading('正在加载表格数据中...');
            },
            onloaded: function () {
                LG.hideLoading();
            }
        });
    };

    //查找是否存在某一个按钮
    LG.findToolbarItem = function (grid, itemID) {
        if (!grid.toolbarManager) return null;
        if (!grid.toolbarManager.options.items) return null;
        var items = grid.toolbarManager.options.items;
        for (var i = 0, l = items.length; i < l; i++) {
            if (items[i].id == itemID) return items[i];
        }
        return null;
    };


    //设置grid的双击事件(带权限控制)
    LG.setGridDoubleClick = function (grid, btnID, btnItemClick) {
        btnItemClick = btnItemClick || toolbarBtnItemClick;
        if (!btnItemClick) return;
        grid.bind('dblClickRow', function (rowdata) {
            var item = LG.findToolbarItem(grid, btnID);
            if (!item) return;
            grid.select(rowdata);
            btnItemClick(item);
        });
    };
    
    LG.RedictLogin=function()
    {
    	alert("请求错误，请重新登录");
    	window.top.location.href="rest/login"; 
    };

    //模糊匹配
    LG.autoComplete = function(urlOrData,txtInput,valInput, options, callback,backspace_callback,cleaninput_callback) 
    {
	   	 var opt = options || {};
	   	 
	   	 var isUrl = typeof urlOrData == "string"; 
	        if(isUrl)       
	        	opt.dataType="json" || options.dataType;
	        else
	        	opt.dataType ="text" || options.dataType;
	        
	       opt.minChars = typeof options.minChars =="number" ? options.minChars : 1;
	       opt.max = typeof options.max =="number" ? options.max : 20;  
	       opt.width =  typeof options.width =="number" ? options.width : 180;
	       opt.multiple =typeof options.multiple =="boolean" ? options.multiple : false;	 
	       $("#"+ txtInput).autocomplete(
	    		   urlOrData,
		        	{
						dataType:opt.dataType,
						minChars:opt.minChars,
						max:opt.max,
						width:opt.width,
						multiple:opt.multiple,
						valInput:valInput,
						parse: function(data) {  
	                        return $.map(data, function(row) {    
	                            return {    
	                                data: row,    
	                                value: row.id.toString(),    
	                                result: row.text    
	                            }    
	                        });    
	                    },   
						formatItem:function(data, i, max)
						{ //下拉显示
							if(typeof(data.unitName)!="undefined")
							{
								return data.text + ' [' + data.unitName + ']';								
							}else
							{
								return data.text;
							}	  
						},
						 
						formatMatch: function(data, i, max) 
						{//配合formatItem使用，作用在于，由于使用了formatItem，所以条目中的内容有所改变，而我们要匹配的是原始的数据，所以用formatMatch做一个调整，使之匹配原始数据
							return data.text + data.id;
						},
						formatResult: function(data) 
						{//定义最终返回的数据，比如我们还是要返回原始数据，而不是formatItem过的数据 						 
							return data.text;
						}			
					}
	       ).result(function(event,data,formatted){  	    	   
						 $("#"+valInput).val(data.id); 
						 if (callback)
						 {
				            callback(data);
						 }  
	    		   }
	      ).delbackspace(function(event){
	    	 var kcode=event.keyCode; 
	    	 if(kcode==8 ||kcode==46 || kcode==110)
	    	 {
	    		 if(backspace_callback)
	    		 {
	    			 backspace_callback();
	    		 } 
	    	 }
	      	}
	     ).cleaninput(function(event){
		    	 if(cleaninput_callback)
	    		 {
		    		 cleaninput_callback();
	    		 } 
	        }
	     ); 
    };
    
    //fixing the IE window resize bug
    $.fn.wresize = function (f) {
        version = '1.1';
        wresize = { fired: false, width: 0 };
        function resizeOnce() {
            if ($.browser.msie) {
                if (!wresize.fired) {
                    wresize.fired = true;
                }
                else {
                    var version = parseInt($.browser.version, 10);
                    wresize.fired = false;
                    if (version < 7) {
                        return true;
                    }
                    else if (version == 7) {
                        //a vertical resize is fired once, an horizontal resize twice
                        var width = $(window).width();
                        if (width != wresize.width) {
                            wresize.width = width;
                            return true;
                        }
                    }
                }
            }
            return true;
        }

        function handleWResize(e) {
            if (resizeOnce()) {
                return f.apply(this, [e]);
            }
        }

        this.each(function () {
            if (this == window) {
                $(this).resize(handleWResize);
            }
            else {
                $(this).resize(f);
            }
        });
        return this;
    }; 
})(jQuery);
