// O'zbekiston viloyatlari GeoJSON ma'lumotlari (soddalashtirilgan)
// Haqiqiy GeoJSON ma'lumotlari katta bo'lgani uchun, bu yerda asosiy struktura

const uzbekistanViloyatlari = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": { "name": "Toshkent", "name_uz": "Toshkent", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [69.0, 41.2], [69.5, 41.2], [69.5, 41.4], [69.0, 41.4], [69.0, 41.2]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Toshkent viloyati", "name_uz": "Toshkent viloyati", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [68.5, 40.5], [70.5, 40.5], [70.5, 41.5], [68.5, 41.5], [68.5, 40.5]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Andijon", "name_uz": "Andijon", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [72.0, 40.5], [72.5, 40.5], [72.5, 41.0], [72.0, 41.0], [72.0, 40.5]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Buxoro", "name_uz": "Buxoro", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [63.5, 39.0], [65.0, 39.0], [65.0, 40.5], [63.5, 40.5], [63.5, 39.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Farg'ona", "name_uz": "Farg'ona", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [70.5, 40.0], [72.0, 40.0], [72.0, 40.8], [70.5, 40.8], [70.5, 40.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Jizzax", "name_uz": "Jizzax", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [67.0, 40.0], [68.5, 40.0], [68.5, 40.8], [67.0, 40.8], [67.0, 40.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Qashqadaryo", "name_uz": "Qashqadaryo", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [65.0, 38.0], [67.0, 38.0], [67.0, 39.5], [65.0, 39.5], [65.0, 38.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Navoiy", "name_uz": "Navoiy", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [64.0, 39.5], [66.0, 39.5], [66.0, 40.5], [64.0, 40.5], [64.0, 39.5]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Namangan", "name_uz": "Namangan", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [71.0, 40.5], [72.0, 40.5], [72.0, 41.2], [71.0, 41.2], [71.0, 40.5]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Samarqand", "name_uz": "Samarqand", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [66.0, 39.0], [68.0, 39.0], [68.0, 40.2], [66.0, 40.2], [66.0, 39.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Sirdaryo", "name_uz": "Sirdaryo", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [68.0, 40.2], [69.5, 40.2], [69.5, 41.0], [68.0, 41.0], [68.0, 40.2]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Surxondaryo", "name_uz": "Surxondaryo", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [66.5, 37.0], [68.5, 37.0], [68.5, 38.5], [66.5, 38.5], [66.5, 37.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Qoraqalpog'iston", "name_uz": "Qoraqalpog'iston", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [56.0, 41.5], [60.0, 41.5], [60.0, 45.5], [56.0, 45.5], [56.0, 41.5]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": { "name": "Xorazm", "name_uz": "Xorazm", "type": "viloyat" },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [60.0, 41.0], [61.5, 41.0], [61.5, 42.0], [60.0, 42.0], [60.0, 41.0]
                ]]
            }
        }
    ]
};

// Viloyat ranglari
const viloyatRanglari = {
    "Toshkent": "#3B82F6",
    "Toshkent viloyati": "#60A5FA",
    "Andijon": "#10B981",
    "Buxoro": "#F59E0B",
    "Farg'ona": "#8B5CF6",
    "Jizzax": "#EC4899",
    "Qashqadaryo": "#14B8A6",
    "Navoiy": "#F97316",
    "Namangan": "#06B6D4",
    "Samarqand": "#6366F1",
    "Sirdaryo": "#84CC16",
    "Surxondaryo": "#EF4444",
    "Qoraqalpog'iston": "#64748B",
    "Xorazm": "#A855F7"
};

