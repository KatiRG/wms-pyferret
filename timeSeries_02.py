
<script type="text/javascript">
    Bokeh.$(function() {
    Bokeh.safely(function() {
        var docs_json = {"840cf7cb-209e-42e2-9d01-66321e583c2e":{"roots":{"references":[{"attributes":{"callback":null,"column_names":["var","date","datestr"],"data":{"date":[],"datestr":[],"var":[]}},"id":"384866b7-0694-44a8-8c32-56369d7b096a","type":"ColumnDataSource"},{"attributes":{"formatter":{"id":"6d4cd82b-0563-4dab-b590-39f07a2501c8","type":"DatetimeTickFormatter"},"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"},"ticker":{"id":"a9927b1e-57de-41eb-b1ae-15da08f51f6b","type":"DatetimeTicker"}},"id":"59a4e373-7aba-4054-86e1-1fe2a1e69a60","type":"DatetimeAxis"},{"attributes":{"formatter":{"id":"4d634081-31ca-4273-94d3-cf02bf5f83b5","type":"BasicTickFormatter"},"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"},"ticker":{"id":"2502f318-5916-4c93-b278-6d3540a4e26b","type":"BasicTicker"}},"id":"127a9680-24fe-48c6-8a66-e99ab2668f65","type":"LinearAxis"},{"attributes":{"months":[0,4,8]},"id":"59d3d812-a7d8-4bb9-a7ba-7fe334d6df28","type":"MonthsTicker"},{"attributes":{"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"}},"id":"ff2d2d60-4c71-4315-9e39-2e56b6ea4cc7","type":"WheelZoomTool"},{"attributes":{"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"}},"id":"a3e78bed-6923-48b7-8356-cce80abe0685","type":"PanTool"},{"attributes":{"line_color":{"value":"#8c564b"},"line_join":"round","x":{"field":"date"},"y":{"field":"var"}},"id":"4bd50f18-5a80-421e-88ed-fa9fa606c2ee","type":"Line"},{"attributes":{"max_interval":500.0,"num_minor_ticks":0},"id":"cb53622e-4905-4958-8323-bf48b39f3d81","type":"AdaptiveTicker"},{"attributes":{"months":[0,1,2,3,4,5,6,7,8,9,10,11]},"id":"f5d498d2-b0db-4a89-ad05-5dea4ff7986a","type":"MonthsTicker"},{"attributes":{"days":[1,15]},"id":"6b1f1fb8-1d99-4513-a49d-5d929c3a590b","type":"DaysTicker"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":3},"x":{"field":"date"},"y":{"field":"var"}},"id":"8527221e-fcac-4743-95cc-176fae8ebb90","type":"Circle"},{"attributes":{"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"}},"id":"e7959029-7306-4672-8480-66fa2f6a17ad","type":"SaveTool"},{"attributes":{"base":24,"mantissas":[1,2,4,6,8,12],"max_interval":43200000.0,"min_interval":3600000.0,"num_minor_ticks":0},"id":"1733f8f7-1e54-4581-b2bb-dff3ae52278a","type":"AdaptiveTicker"},{"attributes":{"data_source":{"id":"384866b7-0694-44a8-8c32-56369d7b096a","type":"ColumnDataSource"},"glyph":{"id":"4bd50f18-5a80-421e-88ed-fa9fa606c2ee","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"d654058e-ecd0-4cd6-843c-6a597341c9d3","type":"Line"},"selection_glyph":null},"id":"943079ad-c504-4125-90e4-2fe93631dec1","type":"GlyphRenderer"},{"attributes":{"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"}},"id":"fe99b2fc-75fc-4250-aae7-0ae725df7936","type":"CrosshairTool"},{"attributes":{"base":60,"mantissas":[1,2,5,10,15,20,30],"max_interval":1800000.0,"min_interval":1000.0,"num_minor_ticks":0},"id":"a29984b1-1854-4619-b7d2-de5ba50f8aca","type":"AdaptiveTicker"},{"attributes":{"months":[0,6]},"id":"4eca82da-90d6-49cb-a68f-f1668e95d1eb","type":"MonthsTicker"},{"attributes":{"days":["%d-%b-%y"],"hours":["%H:%M"],"months":["%b-%y"]},"id":"6d4cd82b-0563-4dab-b590-39f07a2501c8","type":"DatetimeTickFormatter"},{"attributes":{"fill_color":{"value":"#8c564b"},"line_color":{"value":"#8c564b"},"size":{"units":"screen","value":3},"x":{"field":"date"},"y":{"field":"var"}},"id":"3ff0e5d4-4553-4eca-9a6a-d8eca54189b3","type":"Circle"},{"attributes":{"below":[{"id":"59a4e373-7aba-4054-86e1-1fe2a1e69a60","type":"DatetimeAxis"}],"left":[{"id":"127a9680-24fe-48c6-8a66-e99ab2668f65","type":"LinearAxis"}],"min_border":10,"plot_height":500,"plot_width":800,"renderers":[{"id":"59a4e373-7aba-4054-86e1-1fe2a1e69a60","type":"DatetimeAxis"},{"id":"01735b87-1ec8-4409-a737-e37fa5541e4e","type":"Grid"},{"id":"127a9680-24fe-48c6-8a66-e99ab2668f65","type":"LinearAxis"},{"id":"09cab8c2-c37f-4946-b6aa-ba45377d54e5","type":"Grid"},{"id":"831ac5f3-5e32-470f-ad33-36839739c442","type":"Legend"},{"id":"943079ad-c504-4125-90e4-2fe93631dec1","type":"GlyphRenderer"},{"id":"5a95b4ac-13cb-43f6-b76f-9851f2e17271","type":"GlyphRenderer"}],"title":{"id":"ee21c2fe-6fb1-400b-befe-f28fb7757290","type":"Title"},"tool_events":{"id":"228eaee2-247b-420d-bb4c-73d6e3c3843f","type":"ToolEvents"},"toolbar":{"id":"ac1ebec6-a6a3-43fb-a49c-a64cb579a4c1","type":"Toolbar"},"x_range":{"id":"bd255261-bc49-4bdd-b634-6afc0a47f2b6","type":"DataRange1d"},"y_range":{"id":"66b6413c-087b-4a9d-b2a5-887eb72c56c0","type":"DataRange1d"}},"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"de623cf7-49fd-4fe9-a494-fa0ed65fd9f3","type":"YearsTicker"},{"attributes":{"callback":null,"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"},"tooltips":[["date, var","(@datestr, @var)"]]},"id":"cb0c777c-9b46-4021-9df7-5d660ae8fd7c","type":"HoverTool"},{"attributes":{"callback":null},"id":"66b6413c-087b-4a9d-b2a5-887eb72c56c0","type":"DataRange1d"},{"attributes":{"days":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]},"id":"c65f62cb-44d3-4e99-b979-69135b1669dc","type":"DaysTicker"},{"attributes":{"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"}},"id":"68e811ae-4e4e-4df1-9ba7-f1823ebd4add","type":"ResetTool"},{"attributes":{"items":[{"id":"b67d9862-231c-4251-99d9-baf0385ff8c4","type":"LegendItem"}],"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"}},"id":"831ac5f3-5e32-470f-ad33-36839739c442","type":"Legend"},{"attributes":{"months":[0,2,4,6,8,10]},"id":"cfec1e03-fa69-4ab4-ba3d-a8dd5800238d","type":"MonthsTicker"},{"attributes":{"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"}},"id":"ff0b057c-1ac7-4ef3-a58f-1924ffebd83c","type":"ResizeTool"},{"attributes":{"days":[1,8,15,22]},"id":"10e8103d-dd16-4f34-8da6-db7d8a675103","type":"DaysTicker"},{"attributes":{"callback":null},"id":"bd255261-bc49-4bdd-b634-6afc0a47f2b6","type":"DataRange1d"},{"attributes":{},"id":"4d634081-31ca-4273-94d3-cf02bf5f83b5","type":"BasicTickFormatter"},{"attributes":{"plot":null,"text":null},"id":"ee21c2fe-6fb1-400b-befe-f28fb7757290","type":"Title"},{"attributes":{"dimension":1,"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"},"ticker":{"id":"2502f318-5916-4c93-b278-6d3540a4e26b","type":"BasicTicker"}},"id":"09cab8c2-c37f-4946-b6aa-ba45377d54e5","type":"Grid"},{"attributes":{"num_minor_ticks":5},"id":"a9927b1e-57de-41eb-b1ae-15da08f51f6b","type":"DatetimeTicker"},{"attributes":{},"id":"228eaee2-247b-420d-bb4c-73d6e3c3843f","type":"ToolEvents"},{"attributes":{"days":[1,4,7,10,13,16,19,22,25,28]},"id":"bdd74421-e3a3-4370-a08f-59f7cfcca30e","type":"DaysTicker"},{"attributes":{},"id":"2502f318-5916-4c93-b278-6d3540a4e26b","type":"BasicTicker"},{"attributes":{"label":{"value":"vwnd"},"renderers":[{"id":"943079ad-c504-4125-90e4-2fe93631dec1","type":"GlyphRenderer"}]},"id":"b67d9862-231c-4251-99d9-baf0385ff8c4","type":"LegendItem"},{"attributes":{"data_source":{"id":"384866b7-0694-44a8-8c32-56369d7b096a","type":"ColumnDataSource"},"glyph":{"id":"3ff0e5d4-4553-4eca-9a6a-d8eca54189b3","type":"Circle"},"hover_glyph":null,"nonselection_glyph":{"id":"8527221e-fcac-4743-95cc-176fae8ebb90","type":"Circle"},"selection_glyph":null},"id":"5a95b4ac-13cb-43f6-b76f-9851f2e17271","type":"GlyphRenderer"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_join":"round","x":{"field":"date"},"y":{"field":"var"}},"id":"d654058e-ecd0-4cd6-843c-6a597341c9d3","type":"Line"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"cb0c777c-9b46-4021-9df7-5d660ae8fd7c","type":"HoverTool"},{"id":"a3e78bed-6923-48b7-8356-cce80abe0685","type":"PanTool"},{"id":"ff0b057c-1ac7-4ef3-a58f-1924ffebd83c","type":"ResizeTool"},{"id":"ff2d2d60-4c71-4315-9e39-2e56b6ea4cc7","type":"WheelZoomTool"},{"id":"fe99b2fc-75fc-4250-aae7-0ae725df7936","type":"CrosshairTool"},{"id":"68e811ae-4e4e-4df1-9ba7-f1823ebd4add","type":"ResetTool"},{"id":"e7959029-7306-4672-8480-66fa2f6a17ad","type":"SaveTool"}]},"id":"ac1ebec6-a6a3-43fb-a49c-a64cb579a4c1","type":"Toolbar"},{"attributes":{"plot":{"id":"632af734-ca40-4cfd-89e1-6eb449734fd3","subtype":"Figure","type":"Plot"},"ticker":{"id":"a9927b1e-57de-41eb-b1ae-15da08f51f6b","type":"DatetimeTicker"}},"id":"01735b87-1ec8-4409-a737-e37fa5541e4e","type":"Grid"}],"root_ids":["632af734-ca40-4cfd-89e1-6eb449734fd3"]},"title":"Bokeh Application","version":"0.12.3"}};
        var render_items = [{"docid":"840cf7cb-209e-42e2-9d01-66321e583c2e","elementid":"ba22d212-7d5c-496a-af78-2e230d0ef89d","modelid":"632af734-ca40-4cfd-89e1-6eb449734fd3"}];
        
        Bokeh.embed.embed_items(docs_json, render_items);
    });
});
</script>

<div class="bk-root">
    <div class="plotdiv" id="ba22d212-7d5c-496a-af78-2e230d0ef89d"></div>
</div>