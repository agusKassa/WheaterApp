<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Twig\Environment;

final class HomeController extends AbstractController
{
    #[Route('/', name: 'app_home')]
    public function index(): Response
    {
        return $this->render('home/index.html.twig');
    }

    #[Route('/api/render-cities', name: 'render_cities', methods: ['POST'])]
    public function renderCities(Request $request, Environment $twig): JsonResponse
    {
        $cities = json_decode($request->getContent(), true) ?? [];
        $html = $twig->render('components/card/_card_wrapper.html.twig', [
            'cities' => $cities,
        ]);

        return new JsonResponse(['html' => $html]);
    }
}
