# 开发思路（想法）
## 通用
- 类
  - 资源索引（资源的标识）: `ResourceID`
  - 服务器信息: `ServerInfo`
- 函数
  - 混淆（减少特征，用以反审查）: `WLER_confuse(src: dict[str, Any], word_list: list[str]) -> dict[str, Any]`
    - 参数
      - `src`: 指定的`dict`
      - `word_list`: 键被替换成的单词将从里面选择。
    - 过程
      1. 将键替换成相同长度的单词
      2. 加入随机个多余的键值对（长度与结果字典中每一个键的长度都不相等）
      3. 拆分字符串
          - 如果值是字符串，将值分段成列表，在列表随机插入随机数据（该值与列表的第一个值的类型不同）。列表中第一个值的类型代表原来值的类型，读取从列表中第二个值开始。
          - 如果值是列表，插入一个列表在该列表第一个值的前面，表示该值本来是列表，与上一步的结果区分开来。
      4. 扰乱字典顺序
  - 反混淆（从混淆的数据中找到有意义的数据）: `WLER_deobfuscate(src: dict[str, Any], original_keys: list[str]) -> dict`
    - 参数
      - `src`: 用`confuse()`混淆的`dict`
      - `original_key_lengths`: `src`被混淆前的键的长度
    - 过程
      1. 获得键的长度`original_key_lengths = [len(key) for key in original_keys]`
      2. 从`src`中筛选出键长度在`original_key_lengths`里面的键`{original_keys[original_key_lengths.index(len(k))]: src[k] for k in src if len(k) in original_key_lengths}`
      3. 如果值为列表，检查列表的第一个值的类型
         - 如果是字符串，则将该列表除了第一个值以外的所有字符串连接起来，将该字符串作为原来的值
         - 如果是列表，则将移除该列表的第一个值

## 客户端
- 函数
  - 人气度评级: `calculate_popularity(resource: ResourceID) -> fractions.Fraction`
    - 参数
      - `resource`: 资源标识
    - 过程
      1. 向各个服务器请求对该资源的关注度（0或1）
      2. 返回每个服务器的关注度总和除以请求成功的服务器数
  - 向服务器发起一次请求: `request(server_info: ServerInfo, message: dict[str, Any], crypto_vers: list[str], res_vers: list[str]) -> dict[str, Any]`
    - 参数
      - `server_info`: 服务器信息。
      - `message`: 消息。
      - `crypto_vers`: 支持的加密版本。
      - `res_vers`: 支持的响应版本。
    - 返回: 来自服务器的回应（已解密）
    - 消息内容示例: `{"crypto_vers": ["WLER"], "res_vers": ["1.0"], "api": "find_servers", "filters": {"ip_types": ["4", "6"], "protocol": ["http", "https"]}}`
  - 寻找服务器: `find_servers(ip_ranges: list[str], exclude_ips: list[str], servers_dst: list[ServerInfo] | None = None) -> list[ServerInfo]`
    - 参数
      - `ip_ranges`: 寻找服务器的地址范围。CIDR格式。示例: `["0.0.0.0/0"]`
      - `exclude_ips`: 排除的IP地址范围，该列表内的IP地址不会被检测。CIDR格式。示例: `["103.102.166.224/32", "2001:df2:e500:ed1a::1/64"]`
      - `servers_dst`: 已发现的服务器。如果为`None`，则创建一个新列表取而代之(即`server_dst = []`)。如果不为None，则将发现服务器加入该列表。
    - 返回: `servers_dst`
  - 请求资源: `request_resource(resource: ResourceID, servers: list[ServerInfo], progress_dst: list[int] | None = None) -> Resource | int`
    - 参数
      - `resource`: 资源标识。
      - `servers`: 服务器信息。如果一个服务器没有该资源，则请求另一个服务器，直至成功。
      - `progress_dst`: 表示目前在请求第几个服务器（从0算起），list作为指针，可从外部得知进度。如果不为`None`，则`progress_dst[0] = cur_progress`。
    - 返回: 资源本身。如果提供的服务器里没有一个有该资源、或资源校对出错时，返回`None`。

## 服务器
- 常量
  `respond_api: dict[str, Callable] = {"get_resource": respond_resource, "get_follow_status": respond_follow}`
- 函数
  - 对客户端的响应: `respond(raw_json: dict[str, Any], center: dict[str, Any]) -> dict[str, Any]`
    - 描述: 响应客户端的请求。
    - 参数
      - `raw_json`: 来自客户端的原始json。（未经反混淆）
      - `center`: 程序的中心，定义于`main()`
    - 返回: 对客户端的回应（已混淆）
  - 返回资源: `respond_resource(resource: str, **kwargs) -> dict[str, Any]`
    - 参数
      - `resource`: 资源标识的字符串形式
    - 返回示例: `{"ok": 1, "content": "base64..."}`
  - 返回是否关注某一个资源: `respond_follow(resource: str, **kwargs) -> dict[str, Any]`
    - 参数
      - `resource`: 资源标识的字符串形式
    - 返回示例: `{"follow": true}`
