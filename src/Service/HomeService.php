<?php

namespace App\Service;

use Symfony\Contracts\HttpClient\HttpClientInterface;
use Symfony\Contracts\Cache\CacheInterface;
use Symfony\Contracts\Cache\ItemInterface;

class HomeService
{
    private HttpClientInterface $client;
    private CacheInterface $cache;
    private string $apiKey;
    private string $baseUrl;

    public function __construct(HttpClientInterface $client, CacheInterface $cache, string $apiKey)
    {
        $this->client = $client;
        $this->cache = $cache;
        $this->apiKey = $apiKey;
        $this->baseUrl = "https://api.openweathermap.org/data/2.5";
    }

}