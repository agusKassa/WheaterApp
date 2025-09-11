<?php

namespace App\Controller;

use App\Service\WeatherService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Error\SyntaxError;

class WeatherController extends AbstractController
{
    #[Route('/api/weather/current/{city}', name: 'weather_current', methods: ['GET'])]
    public function current(WeatherService $weatherService, string $city): JsonResponse
    {
        $data =$weatherService->getCurrentWeather($city);
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


    #[Route('/api/weather/search', name: 'weather_search')]
    public function search(Request $request, WeatherService $weatherService): Response
    {
        $query = $request->query->get('q', '');

        if (!$query) {
            return $this->json(['error' => 'Ciudad requerida'], 400);
        }

        try {
            $cityWeather = $weatherService->getCurrentWeather($query);
            return $this->json($cityWeather);
        } catch (\Exception $e) {
            return $this->json(['error' => 'Ciudad no encontrada'], 404);
        }
    }


}