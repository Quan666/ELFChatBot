const HOST = "https://api.openai.com";

addEventListener("fetch", (event) => {
    const request = event.request;
    if (request.method === "OPTIONS") {
        // Handle CORS preflight requests
        event.respondWith(handleOptions(request));
    } else {
        // Handle requests to the API server
        event.respondWith(handleRequest(event));
    }
});

const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,HEAD,POST,OPTIONS",
    "Access-Control-Max-Age": "86400",
};

/**
 * Respond to the request
 * @param {Request} request
 */
async function handleRequest(event) {
    const { request } = event;


    //请求头部、返回对象
    let reqHeaders = new Headers(request.headers),
        outBody,
        outStatus = 200,
        outStatusText = "OK",
        outCt = null,
        outHeaders = new Headers({
            "Access-Control-Allow-Origin": reqHeaders.get("Origin"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers":
                reqHeaders.get("Access-Control-Allow-Headers") ||
                "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With, Token, x-access-token, Notion-Version",
        });
    try {
        //取域名第一个斜杠后的所有信息为代理链接
        let url = request.url.substr(8);
        url = decodeURIComponent(url.substr(url.indexOf("/") + 1));

        //需要忽略的代理
        if (
            request.method == "OPTIONS" &&
            reqHeaders.has("access-control-request-headers")
        ) {
            //输出提示
            return new Response(null, PREFLIGHT_INIT);
        } else if (
            url.length < 1 ||
            // url.indexOf(".") == -1 ||
            url == "favicon.ico" ||
            url == "robots.txt"
        ) {
            return Response.redirect("https://chat.openai.com/chat", 301);
        }
        //阻断
        else if (blocker.check(url)) {
            return Response.redirect("https://chat.openai.com/chat", 301);
        } else {
            //补上前缀 http://
            url = url
                .replace(/https:(\/)*/, "https://")
                .replace(/http:(\/)*/, "http://");
            if (url.indexOf("://") == -1) {
                url = `${HOST}/${url}`;
            }
            //构建 fetch 参数
            let fp = {
                method: request.method,
                headers: {},
            };

            //保留头部其它信息
            let he = reqHeaders.entries();
            for (let h of he) {
                if (!["content-length"].includes(h[0])) {
                    fp.headers[h[0]] = h[1];
                }
            }
            // 保留cookie
            if (request.cookies) {
                fp.headers["cookie"] = request.cookies;
            }

            fp.headers["host"] = HOST;
            fp.headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36";

            // 是否带 body
            if (["POST", "PUT", "PATCH", "DELETE"].indexOf(request.method) >= 0) {
                const ct = (reqHeaders.get("content-type") || "").toLowerCase();
                if (ct.includes("application/json")) {
                    let requestJSON = await request.json();
                    fp.body = JSON.stringify(requestJSON);
                } else if (
                    ct.includes("application/text") ||
                    ct.includes("text/html")
                ) {
                    fp.body = await request.text();
                } else if (ct.includes("form")) {
                    // fp.body = await request.formData();
                    fp.body = await request.text();
                } else {
                    fp.body = await request.blob();
                }
            }
            // 发起 fetch
            let fr = await fetch(url, fp);
            // console.log(await fr.text());
            outCt = fr.headers.get("content-type");
            if (outCt.includes("application/text") || outCt.includes("text/html")) {
                try {
                    // 添加base
                    let newFr = new HTMLRewriter()
                        .on("head", {
                            element(element) {
                                element.prepend(`<base href="${url}" />`, {
                                    html: true,
                                });
                            },
                        })
                        .transform(fr);
                    fr = newFr;
                } catch (e) { }
            }
            outStatus = fr.status;
            outStatusText = fr.statusText;
            outBody = fr.body;
        }
    } catch (err) {
        outCt = "application/json";
        outBody = JSON.stringify({
            code: -1,
            msg: JSON.stringify(err.stack) || err,
        });
    }

    //设置类型
    if (outCt && outCt != "") {
        outHeaders.set("content-type", outCt);
    }

    let response = new Response(outBody, {
        status: outStatus,
        statusText: outStatusText,
        headers: outHeaders,
    });

    return response;
}

const blocker = {
    keys: [],
    check: function (url) {
        url = url.toLowerCase();
        let len = blocker.keys.filter((x) => url.includes(x)).length;
        return len != 0;
    },
};

function handleOptions(request) {
    // Make sure the necessary headers are present
    // for this to be a valid pre-flight request
    let headers = request.headers;
    if (
        headers.get("Origin") !== null &&
        headers.get("Access-Control-Request-Method") !== null
        // && headers.get("Access-Control-Request-Headers") !== null
    ) {
        // Handle CORS pre-flight request.
        // If you want to check or reject the requested method + headers
        // you can do that here.
        let respHeaders = {
            ...corsHeaders,
            // Allow all future content Request headers to go back to browser
            // such as Authorization (Bearer) or X-Client-Name-Version
            "Access-Control-Allow-Headers": request.headers.get(
                "Access-Control-Request-Headers"
            ),
        };

        return new Response(null, {
            headers: respHeaders,
        });
    } else {
        // Handle standard OPTIONS request.
        // If you want to allow other HTTP Methods, you can do that here.
        return new Response(null, {
            headers: {
                Allow: "GET, HEAD, POST, OPTIONS",
            },
        });
    }
}
