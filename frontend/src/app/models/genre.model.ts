export interface Genre {
  id: number;
  name_en: string;
  name_ru: string | null;

  slug: string;
  tmdb_name: string | null;
  image_url: string | null;
}
