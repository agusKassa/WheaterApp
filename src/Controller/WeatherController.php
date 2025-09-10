<?php

namespace App\Controller;

use App\Service\WeatherService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Annotation\Route;

class WeatherController extends AbstractController
{
    #[Route('/api/weather/current/{city}', methods: ['GET'])]
    public function current(WeatherService $weatherService, string $city): JsonResponse
    {
        $data =$weatherService->getCurrentWeather($city);
        dd($weatherService->getCurrentWeather($city));
        return $this->json($weatherService->getCurrentWeather($city));
    }

    #[Route('/api/weather/today/{city}', methods: ['GET'])]
    public function today(WeatherService $weatherService, string $city): JsonResponse
    {
        return $this->json($weatherService->getForecastToday($city));
    }

    #[Route('/api/weather/week/{city}', methods: ['GET'])]
    public function week(WeatherService $weatherService, string $city): JsonResponse
    {
        return $this->json($weatherService->getForecastWeek($city));
    }
}