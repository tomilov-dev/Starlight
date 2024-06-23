import { MovieType } from './movie-type.model';

export interface Movie {
  id: number;
  imdb_mvid: string;
  type: MovieType;

  name_en: string;
  name_ru: string | null;
  slug: string;

  is_adult: boolean;
  runtime: number;

  rate: number | null;
  wrate: number | null;
  votes: number | null;

  imdb_extra_added: boolean;
  tmdb_added: boolean;
  image_url: string | null;
}
