worker "fuzzy" {
    backend = "redis";
    expire = 90d;
    allow_update = ["localhost"];
}