local tokens_key = KEYS[1]
local timestamp_key = KEYS[2]

local refill_rate = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local time_now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local fill_time = capacity/refill_rate
local ttl = math.floor(fill_time*2)

local last_tokens = tonumber(redis.call("get", tokens_key))
if last_tokens == nil then
  last_tokens = capacity
end

local time_last_refreshed = tonumber(redis.call("get", timestamp_key))
if time_last_refreshed == nil then
    time_last_refreshed = 0
end

local time_since_refresh = math.max(0, time_now - time_last_refreshed)
local replenished_tokens = time_since_refresh * refill_rate
local filled_tokens = math.min(capacity, last_tokens + replenished_tokens)

local allowed = filled_tokens >= requested
local new_tokens = filled_tokens
if allowed then
  new_tokens = filled_tokens - requested
end

redis.call("setex", tokens_key, ttl, new_tokens)
redis.call("setex", timestamp_key, ttl, time_now)

return { allowed, new_tokens }