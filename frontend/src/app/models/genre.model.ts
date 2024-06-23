import { Movie } from './movie.model';

export interface Genre {
  id: number;
  name_en: string;

  slug: string;
  name_ru: string | null;

  tmdb_name?: string;
  image_url?: string;
}

export interface GenreMovies extends Genre {
  movies: Movie[];
}
