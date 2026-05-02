import { useState, useEffect } from 'react';
import { Combobox } from '@/components/ui/combobox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { metaAPI } from '@/services/api';
import { Loader2 } from 'lucide-react';

interface CityZoneSelectorProps {
  city: string;
  zone: string;
  onCityChange: (city: string) => void;
  onZoneChange: (zone: string) => void;
  error?: string;
}

export function CityZoneSelector({
  city,
  zone,
  onCityChange,
  onZoneChange,
  error,
}: CityZoneSelectorProps) {
  const [cities, setCities] = useState<string[]>([]);
  const [zones, setZones] = useState<string[]>([]);
  const [loadingCities, setLoadingCities] = useState(true);
  const [loadingZones, setLoadingZones] = useState(false);
  const [isCustomCity, setIsCustomCity] = useState(false);
  const [customZone, setCustomZone] = useState('');

  useEffect(() => {
    const loadCities = async () => {
      try {
        const citiesData = await metaAPI.getCities();
        setCities(citiesData);
      } catch (err) {
        console.error('Failed to load cities:', err);
      } finally {
        setLoadingCities(false);
      }
    };
    loadCities();
  }, []);

  useEffect(() => {
    if (city && cities.includes(city)) {
      setIsCustomCity(false);
      const loadZones = async () => {
        setLoadingZones(true);
        try {
          const zonesData = await metaAPI.getZones(city);
          setZones(zonesData);
        } catch (err) {
          console.error('Failed to load zones:', err);
          setZones([]);
        } finally {
          setLoadingZones(false);
        }
      };
      loadZones();
    } else if (city) {
      setIsCustomCity(true);
      setZones([]);
      setLoadingZones(false);
    } else {
      setIsCustomCity(false);
      setZones([]);
      setLoadingZones(false);
    }
  }, [city, cities]);

  const handleCityChange = (newCity: string) => {
    onCityChange(newCity);
    onZoneChange(''); // Reset zone when city changes
    setCustomZone('');
  };

  const handleZoneChange = (newZone: string) => {
    onZoneChange(newZone);
  };

  const handleCustomZoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCustomZone(value);
    onZoneChange(value);
  };

  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="city">City</Label>
        <Combobox
          options={cities}
          value={city}
          onChange={handleCityChange}
          placeholder="Select or type a city"
          allowCreate={true}
          loading={loadingCities}
        />
        {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
      </div>

      <div>
        <Label htmlFor="zone">
          Zone {loadingZones && <Loader2 className="inline h-4 w-4 animate-spin ml-2" />}
        </Label>
        {isCustomCity ? (
          <Input
            id="zone"
            value={customZone}
            onChange={handleCustomZoneChange}
            placeholder="Enter zone"
          />
        ) : (
          <Combobox
            options={zones}
            value={zone}
            onChange={handleZoneChange}
            placeholder="Select zone"
            allowCreate={true}
            loading={loadingZones}
          />
        )}
      </div>
    </div>
  );
}