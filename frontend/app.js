function toggleMeta(el){var p=el.closest(".indicator");if(!p)return;var m=p.querySelector(".ind-meta");if(m)m.classList.toggle("show")}
function editRule(ik){var cur=modifiedParams[ik]||"";var v=prompt("修改参数:",cur);if(v!==null){modifiedParams[ik]=v;refreshData()}}
function resetParams(){modifiedParams={};refreshData()}
var API="/api/data",REFRESH_MS=300000,activeTab="gold",modifiedParams={}

async function refreshData(){
  var b=document.getElementById("updateBadge");
  b.innerHTML='<span class="dot dot-warn"></span>刷新中...'
  try{
    var r=await fetch(API),d=await r.json()
    renderPrices(d);renderChain(d);renderTab(d.tabs,d);renderSummary(d)
    var t=d.button_time||d.update_time||new Date().toLocaleString("zh-CN")
    b.innerHTML='<span class="dot dot-ok"></span>上次更新 '+t
    switchTab(activeTab)
  }catch(e){b.innerHTML='<span class="dot dot-warn"></span>数据加载失败'}
}

function renderPrices(d){
  var p=d.prices;var el=document.getElementById("priceStrip")
  if(!p||!p.gold){el.innerHTML='<div class="skeleton-wide">数据失效</div>';return}
  var r=d.ratio||"N/A"
  el.innerHTML=Object.entries({gold:"伦敦金现货",silver:"伦敦银现货"}).map(function(e){
    var k=e[0],lb=e[1],px=p[k];if(!px||px.error)return""
    var cl=px.change_pct>=0?"up":"down",sg=px.change_pct>=0?"+":""
    var sup=k==="gold"?d.gold_support:d.silver_support
    var res=k==="gold"?d.gold_resistance:d.silver_resistance
    var ext=""
    if(k==="gold"){
      ext='<div class="price-domestic">国内金价: <span>¥'+p.domestic_gold+'/g</span></div>'
      if(p.shfe_gold)ext+='<div class="price-ext">沪金主力: <span>¥'+p.shfe_gold.price+'/g</span></div>'
    }else{
      if(p.shfe_silver)ext='<div class="price-ext">沪银主力: <span>¥'+p.shfe_silver.price+'/吨</span></div>'
    }
    return '<div class="price-card '+k+'"><div class="price-info"><div class="price-label">'+lb+'</div><div class="price-row"><div class="price-value">$'+px.price+'</div><div class="price-change '+cl+'">'+sg+px.change_pct.toFixed(2)+'%</div></div>'+ext+'</div><div class="price-meta">支撑 $'+sup+'<br>阻力 $'+res+'<br>金银比 '+r+'</div></div>'
  }).join("")
}function renderChain(d){
  var el=document.getElementById("macroChain")
  if(d.macro_chain)el.innerHTML='<strong>宏观逻辑链:</strong> '+d.macro_chain
  else el.innerHTML=''
}

function renderTab(tabs, d){
  if(!tabs)return
  Object.keys(tabs).forEach(function(k){
    var el=document.getElementById("tabContent-"+k);if(!el)return
    var order=["macro","capital_flow","supply_demand","ratio_technical","geopolitics"]
    var h='<div class="monitor-grid">'
    order.forEach(function(dk){
      var dim=tabs[k][dk];if(!dim)return
      var title=dim.title||dk;var pr=dim.priority||"";var pc=dim.cls||"low"
      var isFull=dk==="macro"
      h+='<div class="dim-card'+(isFull?" full":"")+'">'
      h+='<div class="dim-header"><div class="dim-title">'+title+'</div><div class="dim-priority '+pc+'">'+pr+'</div></div>'
      // Build a list of indicator keys in order of their predefined order
      var indKeys=Object.keys(dim.indicators)
      indKeys.forEach(function(ik){
        var iv=dim.indicators[ik]
        if(!iv||!iv.name)return
        var nm=iv.name;var val=iv.value||"N/A"
        var imp=iv.impacted||"Pending"
        var stMap={Bullish:"利多",Bearish:"利空",Watch:"关注",Neutral:"中性",Pending:"待查",Reference:"参考"}
        var stLabel=stMap[imp]||imp
        var scMap={Bullish:"bullish",Bearish:"bearish",Watch:"watch",Neutral:"neutral",Pending:"pending",Reference:"reference"}
        var sc=scMap[imp]||"neutral"
        var conc=iv.conclusion||"";if(conc==""||conc.includes("暂无")||conc.includes("待")||(conc&&!/[\u4e00-\u9fff]/.test(conc))){var at=(d&&d.analysis_texts?d.analysis_texts[ik]:"");if(at){conc=at}}
        var src=iv.source?' <a href="'+iv.source+'" target="_blank" class="ind-source" title="查看数据来源">↳</a>':""
        var thres=iv.threshold||""
        var interp=iv.interpretation||""
        var freq=iv.frequency||""
        h+='<div class="indicator"><div class="ind-row">'
        h+='<span class="ind-name" title="'+nm+'">'+nm+src+'</span>'
        h+='<span class="ind-value">'+val+'</span>'
        h+='<span class="ind-status status-'+sc+'">'+stLabel+'</span>'
        h+='</div><div class="ind-row-conclusion"><span class="ind-conclusion">'+conc+'</span>'
        h+='<span class="ind-toggle" onclick="toggleMeta(this)" title="展开详情">▼</span></div>'
        // Metadata panel
        h+='<div class="ind-meta">'
        if(thres)h+='<div><span class="meta-label">阈值: </span><span class="meta-val">'+thres+'</span></div>'
        if(interp)h+='<div><span class="meta-label">解读: </span><span class="meta-bull">'+interp+'</span></div>'
        if(freq)h+='<div><span class="meta-label">监测频率: </span><span class="meta-val">'+freq+'</span></div>'
        var at=(d&&d.analysis_texts?d.analysis_texts[ik]:'')||iv.conclusion||'';if(at)h+='<div><span class="meta-label">系统分析: </span><span class="meta-val">'+at+'</span></div>'
        if(stLabel)h+='<div><span class="meta-label">判定结果: </span><span class="meta-bull">'+stLabel+'</span></div>'
        h+='</div></div>'
      })
      h+='</div>'
    })
    h+='</div>';el.innerHTML=h
  })
}

function renderSummary(d){
  var el=document.getElementById("summarySection");if(!el)return
  var tabs=d.tabs;if(!tabs){el.innerHTML="";return}
  var bullish=[],bearish=[],watch=[]
  Object.keys(tabs).forEach(function(k){
    Object.keys(tabs[k]).forEach(function(dk){
      var dim=tabs[k][dk]
      Object.keys(dim.indicators).forEach(function(ik){
        var iv=dim.indicators[ik];if(!iv||!iv.name)return
        var nm=iv.name;var imp=iv.impacted||"";var desc=iv.conclusion||""
        var label=nm+(desc?" - "+desc:"")
        if(imp==="Bullish")bullish.push(label)
        else if(imp==="Bearish")bearish.push(label)
        else if(imp==="Watch"||imp==="Pending")watch.push(label)
      })
    })
  })
  bullish=[...new Set(bullish)];bearish=[...new Set(bearish)];watch=[...new Set(watch)]
  var h='<div class="summary-title">📋 综合观察总结</div><div class="summary-grid">'
  h+='<div class="summary-col bull"><div class="summary-col-label">▲ 利多因素 ('+bullish.length+')</div><ul>'
  bullish.slice(0,15).forEach(function(s){h+='<li>'+s+'</li>'})
  h+='</ul></div>'
  h+='<div class="summary-col bear"><div class="summary-col-label">▼ 利空因素 ('+bearish.length+')</div><ul>'
  bearish.slice(0,15).forEach(function(s){h+='<li>'+s+'</li>'})
  h+='</ul></div>'
  h+='<div class="summary-col watch"><div class="summary-col-label">○ 关注事项 ('+watch.length+')</div><ul>'
  watch.slice(0,15).forEach(function(s){h+='<li>'+s+'</li>'})
  h+='</ul></div></div>';el.innerHTML=h
}

function switchTab(tab){
  activeTab=tab
  document.querySelectorAll(".tab-btn").forEach(function(b){b.classList.toggle("active",b.dataset.tab===tab)})
  document.querySelectorAll(".tab-panel").forEach(function(p){p.classList.toggle("active",p.id==="tabContent-"+tab)})
}
document.addEventListener("DOMContentLoaded",function(){refreshData();setInterval(refreshData,REFRESH_MS)})