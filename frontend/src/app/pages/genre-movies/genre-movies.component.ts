import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { IMDbMovieBase } from '../../models/base.movie.model';
import { Genre } from '../../models/genre.model';
import { DataService } from '../../services/data.service';

@Component({
  selector: 'app-genre-movies',
  templateUrl: './genre-movies.component.html',
  styleUrl: './genre-movies.component.css',
})
export class GenreMoviesComponent implements OnInit {
  slug: string = '';
  genre: Genre | undefined;
  movies: IMDbMovieBase[] = [];

  page: number = 1;
  pageSize: number = 10;
  totalMovies: number = 0;

  constructor(
    private route: ActivatedRoute,
    private dataService: DataService
  ) {}

  ngOnInit(): void {
    this.slug = this.route.snapshot.params['slug'];
    this.genre = this.dataService.getGenre(this.slug);
    this.loadMoviesByGenre();
  }

  loadMoviesByGenre() {
    this.dataService
      .getMoviesByGenre(this.slug, this.page, this.pageSize)
      .subscribe({
        next: (data) => {
          this.movies = data;
        },
        error: (error) => {
          console.error("Can't request genres from api!", error);
        },
      });
  }

  onPageChange(newPage: number): void {
    if (newPage <= 1) {
      return;
    }

    this.page = newPage;
    this.loadMoviesByGenre();
  }
}
