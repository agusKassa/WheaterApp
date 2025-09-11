<?php

namespace App\Twig;

use Twig\Extension\AbstractExtension;
use Twig\TwigFunction;
use Symfony\Component\Asset\Packages;
use Twig\Environment;

class IconExtension extends AbstractExtension
{
    private Packages $assets;
    private Environment $twig;

    public function __construct(Packages $assets, Environment $twig)
    {
        $this->assets = $assets;
        $this->twig = $twig;
    }

    public function getFunctions(): array
    {
        return [
            new TwigFunction('weather_icon', [$this, 'getWeatherIcon'], ['is_safe' => ['html']]),
            new TwigFunction('wind_arrow', [$this, 'getWindArrow'], ['is_safe' => ['html']]),
        ];
    }

    public function getWeatherIcon(string $icon): string
    {
        $iconKey = strtolower($icon);
        $map = [
            'clear'  => 'sun.svg',
            'rain'   => 'cloud-rain.svg',
            'cloud'  => 'cloud.svg',
            'clouds' => 'cloud.svg', // a veces viene en plural
        ];
        $file = $map[$iconKey] ?? 'sun.svg';
        $url = $this->assets->getUrl('svg/' . $file);
        return sprintf('<img src="%s" alt="%s" class="icon-weather">', $url, $iconKey);
    }


    public function getWindArrow(string $direction): string
    {
        $direction = strtoupper($direction);
        $map = [
            'N'   => 'arrow-up',
            'NNE' => 'arrow-up-right',
            'NE'  => 'arrow-up-right',
            'ENE' => 'arrow-up-right',

            'E'   => 'arrow-right',
            'ESE' => 'arrow-down-right',
            'SE'  => 'arrow-down-right',
            'SSE' => 'arrow-down-right',

            'S'   => 'arrow-down',
            'SSW' => 'arrow-down-left',
            'SW'  => 'arrow-down-left',
            'WSW' => 'arrow-down-left',

            'W'   => 'arrow-left',
            'WNW' => 'arrow-up-left',
            'NW'  => 'arrow-up-left',
            'NNW' => 'arrow-up-left',
        ];

        $arrow = $map[$direction] ?? 'arrow-up';

        return $this->twig->render('components/arrows/' . $arrow . '.html.twig');
    }
}
