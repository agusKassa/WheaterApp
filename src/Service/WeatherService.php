<?php

namespace App\Service;

use App\Api\WeatherReportDTO;
use Symfony\Contracts\HttpClient\HttpClientInterface;
use Symfony\Contracts\Cache\CacheInterface;
use Symfony\Contracts\Cache\ItemInterface;

class WeatherService
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

    public function getCurrentWeather(string $city): WeatherReportDTO
    {
        return $this->cache->get("weather_current_$city", function (ItemInterface $item) use ($city) {
            $item->expiresAfter(600); // 10 minutos de cache
            $response = $this->client->request("GET", "{$this->baseUrl}/weather", [
                "query" => [
                    "q" => $city,
                    "appid" => $this->apiKey,
                    "units" => "metric",
                    "lang" => "es"
                ]
            ]);
            return $this->makeWeatherDTo($response->toArray());
        });
    }

    public function getForecastToday(string $city): array
    {
        return $this->cache->get("weather_today_$city", function (ItemInterface $item) use ($city) {
            $item->expiresAfter(600);

            $response = $this->client->request("GET", "{$this->baseUrl}/forecast", [
                "query" => [
                    "q" => $city,
                    "appid" => $this->apiKey,
                    "units" => "metric",
                    "lang" => "es",
                    "cnt" => 8 // ~24hs (cada 3h)
                ]
            ]);

            return $response->toArray();
        });
    }

    public function getForecastWeek(string $city): array
    {
        return $this->cache->get("weather_week_$city", function (ItemInterface $item) use ($city) {
            $item->expiresAfter(600);

            $response = $this->client->request("GET", "{$this->baseUrl}/forecast", [
                "query" => [
                    "q" => $city,
                    "appid" => $this->apiKey,
                    "units" => "metric",
                    "lang" => "es",
                ]
            ]);

            return $response->toArray();
        });
    }

    public function windDirection(int $deg): string
    {
        $directions = [
            "N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW",
            "W", "WNW", "NW", "NNW"
        ];

        // Cada sector cubre 22.5° (360 / 16)
        $index = (int) round($deg / 22.5) % 16;

        return $directions[$index];
    }

    public function makeWeatherDTo($data) : WeatherReportDTO
    {
        $report = new WeatherReportDTO();
        $report->id = $data["id"];
        $report->city = $data['name'];
        $report->country = $data['sys']['country'];
        $report->temp = $data['main']['temp'];
        $report->feels_like = $data['main']['feels_like'];
        $report->temp_min = $data['main']['temp_min'];
        $report->temp_max = $data['main']['temp_max'];
        $report->visibility = ($data['visibility']/100);
        $report->humidity = $data['main']['humidity'];
        $report->wind_speed = $data['wind']['speed'];
        $report->wind_direction = $this->windDirection($data['wind']['deg']);
        $report->icon = $data['weather'][0]['main'];
        return $report;
    }
}