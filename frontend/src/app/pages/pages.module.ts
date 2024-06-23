import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HomePageComponent } from './home-page/home-page.component';
import { ComponentsModule } from '../components/components.module';
import { GenresComponent } from './genres/genres.component';
import { SearchComponent } from './search/search.component';
import { RouterModule } from '@angular/router';
import { GenreMoviesComponent } from './genre-movies/genre-movies.component';

@NgModule({
  declarations: [
    HomePageComponent,
    GenresComponent,
    SearchComponent,
    GenreMoviesComponent,
  ],
  imports: [CommonModule, ComponentsModule, RouterModule],
  exports: [
    HomePageComponent,
    GenresComponent,
    SearchComponent,
    GenreMoviesComponent,
  ],
})
export class PagesModule {}
